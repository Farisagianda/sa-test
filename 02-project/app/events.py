import os, json
from collections import deque
from datetime import datetime, timezone
from typing import Optional
from config import settings

EVENT_LOG = deque(maxlen=settings.event_log_max)

def seed_from_disk() -> None:
    try:
        with open(settings.audit_path, "r") as f:
            lines = f.readlines()
        for line in lines[-EVENT_LOG.maxlen:]:
            try:
                EVENT_LOG.append(json.loads(line))
            except Exception:
                continue
    except FileNotFoundError:
        pass

def log_event(kind: str, namespace: str, name: str, msg: str, extra: Optional[dict] = None):
    evt = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        "namespace": namespace,
        "name": name,
        "msg": msg,
        "extra": extra or {},
    }
    EVENT_LOG.appendleft(evt)
    try:
        os.makedirs(os.path.dirname(settings.audit_path), exist_ok=True)
        if os.path.exists(settings.audit_path) and os.path.getsize(settings.audit_path) > settings.audit_max_bytes:
            os.replace(settings.audit_path, settings.audit_path + ".1")
        with open(settings.audit_path, "a") as f:
            f.write(json.dumps(evt) + "\n")
    except Exception:
        pass

def tail(limit: int = 50):
    data = list(EVENT_LOG)
    limit = max(1, min(limit, len(data))) if data else 0
    return data[:limit]