from typing import Optional, List, Tuple
from kubernetes import client, config
from kubernetes.client import ApiException, CustomObjectsApi
from config import settings
from models import EnvSpec
from events import log_event

def init_kube():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()

def ensure_namespace(ns: str):
    core = client.CoreV1Api()
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=ns, labels={"team": ns}))
    try:
        core.create_namespace(body)
    except ApiException as e:
        if e.status != 409:
            raise

def get_pod_metrics(namespace: str, pod: str) -> Optional[Tuple[float, float]]:
    try:
        api = CustomObjectsApi()
        m = api.get_namespaced_custom_object(
            group="metrics.k8s.io", version="v1beta1",
            namespace=namespace, plural="pods", name=pod
        )
        usage = m["containers"][0]["usage"]
        cpu_str, mem_str = usage["cpu"], usage["memory"]

        # cpu to millicores
        if cpu_str.endswith("n"):   cpu_m = int(cpu_str[:-1]) / 1_000_000
        elif cpu_str.endswith("u"): cpu_m = int(cpu_str[:-1]) / 1_000
        elif cpu_str.endswith("m"): cpu_m = int(cpu_str[:-1])
        else:                       cpu_m = int(cpu_str) * 1000

        mem = mem_str.lower()
        if   mem.endswith("ki"): mem_mi = int(mem[:-2]) / 1024
        elif mem.endswith("mi"): mem_mi = int(mem[:-2])
        elif mem.endswith("gi"): mem_mi = int(mem[:-2]) * 1024
        else:                    mem_mi = int(mem) / (1024 * 1024)

        return cpu_m, mem_mi
    except Exception:
        return None

async def apply_k8s_objects(spec: EnvSpec):
    apps = client.AppsV1Api()
    core = client.CoreV1Api()
    ensure_namespace(spec.team)

    labels = {"app": spec.name, "team": spec.team}
    if spec.owner:
        labels["owner"] = spec.owner

    service_type = settings.service_type
    node_port = int(settings.node_port) if (service_type == "NodePort" and settings.node_port.isdigit()) else None
    node_selector = {}
    tolerations: list[client.V1Toleration] = []

    csec = client.V1SecurityContext(
        allow_privilege_escalation=False,
        read_only_root_filesystem=False,
        run_as_non_root=True,
        run_as_user=10001,
        run_as_group=10001,
    )

    container = client.V1Container(
        name="app",
        image=f"{spec.base_image}",
        command=["/bin/sh", "-lc"],
        args=["PYTHONDONTWRITEBYTECODE=1 python3 -m http.server 8080"],
        ports=[client.V1ContainerPort(name="http", container_port=8080)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": spec.cpu, "memory": spec.memory}
        ),
        security_context=csec,
    )

    if spec.pool:
        labels["pool"] = spec.pool
        node_selector["pool"] = spec.pool
        tolerations.append(client.V1Toleration(
            key="pool", operator="Equal", value=spec.pool, effect="NoSchedule"
        ))

    if spec.gpu and spec.gpu > 0:
        limits = {"nvidia.com/gpu": spec.gpu}
        if container.resources and container.resources.limits:
            container.resources.limits.update(limits)
        else:
            container.resources = client.V1ResourceRequirements(
                requests={"cpu": spec.cpu, "memory": spec.memory}, limits=limits
            )
        node_selector["gpu"] = "true"
        tolerations.append(client.V1Toleration(
            key="gpu", operator="Equal", value="true", effect="NoSchedule"
        ))

    psec = client.V1PodSecurityContext(
        run_as_non_root=True,
        run_as_user=10001,
        run_as_group=10001,
        fs_group=10001,
    )

    pod = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=labels),
        spec=client.V1PodSpec(
            security_context=psec,
            containers=[container],
            node_selector=node_selector or None,
            tolerations=tolerations or None,
            priority_class_name=spec.priority or None,
        ),
    )

    dep = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=spec.name, labels=labels),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels=labels),
            template=pod,
        ),
    )

    try:
        apps.create_namespaced_deployment(namespace=spec.team, body=dep)
    except ApiException as e:
        if e.status == 409:
            apps.replace_namespaced_deployment(name=spec.name, namespace=spec.team, body=dep)
        else:
            raise

    svc_port = client.V1ServicePort(name="http", port=8080, target_port="http")
    if node_port is not None:
        svc_port.node_port = node_port

    svc = client.V1Service(
        metadata=client.V1ObjectMeta(name=spec.name, labels=labels),
        spec=client.V1ServiceSpec(
            type=service_type,
            selector=labels,
            ports=[svc_port],
        ),
    )
    try:
        core.create_namespaced_service(namespace=spec.team, body=svc)
    except ApiException as e:
        if e.status == 409:
            core.patch_namespaced_service(name=spec.name, namespace=spec.team, body=svc)
        else:
            raise

    if settings.hpa_enabled:
        autoscaling_api = client.AutoscalingV2Api()
        hpa = client.V2HorizontalPodAutoscaler(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            metadata=client.V1ObjectMeta(
                name=spec.name,
                namespace=spec.team,
                labels=labels,
            ),
            spec=client.V2HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V2CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=spec.name,
                ),
                min_replicas=settings.hpa_min,
                max_replicas=settings.hpa_max,
                behavior=client.V2HorizontalPodAutoscalerBehavior(
                    scale_down=client.V2HPAScalingRules(
                        stabilization_window_seconds=settings.hpa_sd_stab,
                        policies=[client.V2HPAScalingPolicy(
                            type="Percent", value=100, period_seconds=60
                        )],
                    )
                ),
                metrics=[
                    client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="cpu",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=settings.hpa_cpu_util,
                            ),
                        ),
                    ),
                    client.V2MetricSpec(
                        type="Resource",
                        resource=client.V2ResourceMetricSource(
                            name="memory",
                            target=client.V2MetricTarget(
                                type="Utilization",
                                average_utilization=settings.hpa_mem_util,
                            ),
                        ),
                    ),
                ],
            ),
        )

        try:
            autoscaling_api.create_namespaced_horizontal_pod_autoscaler(
                namespace=spec.team, body=hpa
            )
        except ApiException as e:
            if e.status == 409:
                autoscaling_api.replace_namespaced_horizontal_pod_autoscaler(
                    name=spec.name, namespace=spec.team, body=hpa
                )
            else:
                raise

    log_event("create", spec.team, spec.name, "deployment+service ready", {"owner": spec.owner, "pool": spec.pool})