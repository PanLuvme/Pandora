import os
import json
import time
import fcntl
from datetime import datetime
from config import DIAGNOSTICS_PATH, REGISTRY_PATH


def log_metrics(entry: str):
    path = os.path.join(DIAGNOSTICS_PATH, "METRICS.md")
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(f"{ts} | {entry}\n")


def append_to_alerts(entry: str):
    path = os.path.join(DIAGNOSTICS_PATH, "ALERTS.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(entry)


def write_module_health(module_id: str, health: dict):
    health_dir = os.path.join(DIAGNOSTICS_PATH, "modules")
    os.makedirs(health_dir, exist_ok=True)
    health["last_run"] = datetime.now().isoformat()
    path = os.path.join(
        health_dir, f"{module_id}-health.json"
    )
    with open(path, "w") as f:
        json.dump(health, f, indent=2)


def wait_for_file_ready(path: str,
                         timeout: float = 5.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with open(path, "r") as f:
                fcntl.flock(
                    f.fileno(),
                    fcntl.LOCK_SH | fcntl.LOCK_NB
                )
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return True
        except (IOError, OSError):
            time.sleep(0.2)
    return False


def read_registry() -> dict:
    if not os.path.exists(REGISTRY_PATH):
        return {"modules": {}}
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def is_module_enabled(module_id: str) -> bool:
    return (read_registry()
            .get("modules", {})
            .get(module_id, {})
            .get("enabled", False))
