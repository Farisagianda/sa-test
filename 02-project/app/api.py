from fastapi import APIRouter, BackgroundTasks, Request, Query
from typing import Optional, List
from kubernetes import client
from kubernetes.client import ApiException
from models import EnvSpec
from events import log_event, tail as events_tail
from k8s import get_pod_metrics
from config import settings
import json

router = APIRouter()

@router.post("/envs")
async def create_env(spec: EnvSpec, bg: BackgroundTasks):
    log_event("create", spec.team, spec.name, "submitted", {"owner": spec.owner, "pool": spec.pool})
    from k8s import apply_k8s_objects
    bg.add_task(apply_k8s_objects, spec)
    return {"status": "submitted", "name": spec.name}

@router.get("/envs")
def list_envs(team: Optional[str] = None):
    apps = client.AppsV1Api()
    core = client.CoreV1Api()
    selector = f"team={team}" if team else "team"
    deps = apps.list_deployment_for_all_namespaces(label_selector=selector).items

    out: List[dict] = []
    for d in deps:
        ns = d.metadata.namespace
        name = d.metadata.name
        tmpl: client.V1PodTemplateSpec = d.spec.template
        psp: client.V1PodSpec = tmpl.spec
        c = (tmpl.spec.containers or [client.V1Container()])[0]
        req = (c.resources and c.resources.requests) or {}
        owner = (d.metadata.labels or {}).get("owner") or (tmpl.metadata.labels or {}).get("owner")
        node_selector = psp.node_selector or {}
        pool = node_selector.get("pool") or node_selector.get("nodepool")
        priority = psp.priority_class_name or {}
        cpu_used = mem_used = None

        spec = EnvSpec(
            name=name,
            team=ns,
            pool=pool,
            priority=priority or "",
            owner=owner,
            base_image=c.image or "",
            packages=[],
            cpu=(req.get("cpu") or "500m"),
            memory=(req.get("memory") or "1Gi"),
            gpu=0
        )

        svc_str = None
        try:
            s = core.read_namespaced_service(name, ns)
            if s.spec.type == "NodePort":
                ports = ", ".join(str(p.node_port) for p in s.spec.ports or [])
                svc_str = f"NodePort:{ports}"
            else:
                ports = ", ".join(str(p.port) for p in s.spec.ports or [])
                svc_str = f"{s.spec.type or 'ClusterIP'} {s.spec.cluster_ip}:{ports}"
        except ApiException:
            pass

        try:
            pods = core.list_namespaced_pod(namespace=ns, label_selector=f"app={name}").items
            if pods:
                pod_name = pods[0].metadata.name
                m = get_pod_metrics(ns, pod_name)
                if m:
                    cpu_used, mem_used = m
        except Exception:
            pass

        out.append({
            "spec": spec.model_dump(),
            "status": {
                "ready": d.status.ready_replicas or 0,
                "replicas": d.spec.replicas or 0,
                "created": d.metadata.creation_timestamp,
                "service": svc_str,
                "cpu_used_m": cpu_used,
                "mem_used_mi": mem_used,
            }
        })
    return out

@router.delete("/envs/{team}/{name}", status_code=202)
def delete_env(team: str, name: str, owner: Optional[str] = Query(None)):
    apps = client.AppsV1Api()
    core = client.CoreV1Api()

    resolved_owner = owner
    resolved_pool: Optional[str] = None

    try:
        dep = apps.read_namespaced_deployment(name=name, namespace=team)

        meta_lbls = (dep.metadata.labels or {})
        tpl_lbls = (dep.spec.template.metadata.labels or {})
        node_sel = (dep.spec.template.spec.node_selector or {})

        if not resolved_owner:
            resolved_owner = meta_lbls.get("owner") or tpl_lbls.get("owner")

        resolved_pool = (
                meta_lbls.get("pool")
                or tpl_lbls.get("pool")
                or node_sel.get("pool")
        )
    except ApiException:
        pass

    log_event(
        "delete", team, name, "delete requested",
        {"owner": resolved_owner, "pool": resolved_pool}
    )

    try:
        apps.delete_namespaced_deployment(
            name=name, namespace=team, propagation_policy="Foreground"
        )
    except ApiException as e:
        if e.status != 404:
            raise

    try:
        core.delete_namespaced_service(name=name, namespace=team)
    except ApiException as e:
        if e.status != 404:
            raise

    try:
        client.AutoscalingV2Api().delete_namespaced_horizontal_pod_autoscaler(
            name=name, namespace=team
        )
    except ApiException as e:
        if e.status != 404:
            raise

    log_event("delete", team, name, "delete issued (hpa+svc+deploy)", {"owner": resolved_owner, "pool": resolved_pool})
    return {"status": "deleting", "team": team, "name": name}

@router.get("/events")
def get_events(limit: int = 50):
    return events_tail(limit)

@router.post("/alerts")
async def alerts(req: Request):
    body = await req.json()
    apps = client.AppsV1Api()
    for a in body.get("alerts", []):
        lbl = a.get("labels", {})
        if a.get("status") == "firing" and lbl.get("alertname") == "EnvIdleCPU":
            ns = lbl.get("namespace")
            deployment = lbl.get("env") or lbl.get("app")
            if ns and deployment:
                apps.patch_namespaced_deployment_scale(
                    name=deployment, namespace=ns, body={"spec": {"replicas": 0}}
                )
                pool = owner = None
                try:
                    dep = apps.read_namespaced_deployment(deployment, ns)
                    owner = (dep.metadata.labels or {}).get("owner")
                    podspec = dep.spec.template.spec or client.V1PodSpec()
                    node_selector = podspec.node_selector or {}
                    pool = node_selector.get("pool")
                except Exception:
                    pass
                log_event("scale", ns, deployment, "scaled to 0 (EnvIdleCPU firing)", {"owner": owner, "pool": pool})
    return {"ok": True}

@router.get("/audit")
def get_audit(limit: int = Query(100, ge=1, le=1000), team: Optional[str] = None,
              owner: Optional[str] = None, kind: Optional[str] = None):
    rows = []
    try:
        with open(settings.audit_path, "r") as f:
            lines = f.readlines()
        for line in reversed(lines):
            evt = json.loads(line)
            if team  and evt.get("namespace") != team: continue
            if kind  and evt.get("kind")       != kind: continue
            if owner and (evt.get("extra", {}).get("owner") != owner): continue
            rows.append(evt)
            if len(rows) >= limit: break
    except FileNotFoundError:
        pass
    return rows