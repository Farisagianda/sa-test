import os
from pathlib import Path
from dataclasses import dataclass

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return int(default)
    try:
        return int(raw)
    except Exception:
        try:
            return int(float(raw))
        except Exception:
            return int(default)

@dataclass(frozen=True)
class Settings:
    base_dir: Path = Path(__file__).resolve().parent
    static_dir: Path = base_dir / "static"

    event_log_max: int = _env_int("EVENT_LOG_MAX", 200)
    audit_path: str = os.getenv("AUDIT_PATH", "/data/audit.jsonl")
    audit_max_bytes: int = _env_int("AUDIT_MAX_BYTES", 5_242_880)

    service_type: str = os.getenv("SERVICE_TYPE", "ClusterIP")
    node_port: str = os.getenv("NODE_PORT", "").strip()

    hpa_enabled: bool = os.getenv("HPA_ENABLED", "true").lower() == "true"
    hpa_min: int      = _env_int("HPA_MIN", 1)
    hpa_max: int      = _env_int("HPA_MAX", 5)
    hpa_cpu_util: int = _env_int("HPA_CPU_UTIL", 70)
    hpa_mem_util: int = _env_int("HPA_MEM_UTIL", 80)
    hpa_sd_stab: int  = _env_int("HPA_SD_STAB", 60)

settings = Settings()