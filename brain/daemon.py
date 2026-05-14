import os
import sys
import time
import threading
import json
import socket
import subprocess
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import schedule

from config import (
    VAULT_PATH, DEBOUNCE_SECONDS, MCP_PORT, REGISTRY_PATH
)
from utils import log_metrics, append_to_alerts


class DebouncedVaultWatcher(FileSystemEventHandler):
    def __init__(self):
        self._pending = {}
        self._lock = threading.Lock()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".md"):
            self._debounce(event.src_path, "created")

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return
        if "REGISTRY.json" in event.src_path:
            return
        if "70_Diagnostics" in event.src_path:
            return
        if ".git" in event.src_path:
            return
        self._debounce(event.src_path, "modified")

    def _debounce(self, path: str, event_type: str):
        with self._lock:
            if path in self._pending:
                self._pending[path].cancel()
            timer = threading.Timer(
                DEBOUNCE_SECONDS,
                self._process,
                args=[path, event_type]
            )
            self._pending[path] = timer
            timer.start()

    def _process(self, path: str, event_type: str):
        with self._lock:
            self._pending.pop(path, None)
        if ".sync-conflict" in path:
            alert = (
                f"\n- [ ] Sync conflict: {path}\n"
                f"      Resolve manually — "
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            append_to_alerts(alert)
            return
        from utils import wait_for_file_ready
        if not wait_for_file_ready(path):
            return
        if "/00_Inbox/" in path or "\\00_Inbox\\" in path:
            log_metrics(f"inbox_detected | path:{path}")
            print(f"Inbox: {path}")
        elif "/10_Atomic/" in path or "\\10_Atomic\\" in path:
            print(f"Syncing: {path}")
            venv_python = os.path.expanduser(
                "~/Pandora/brain/venv/bin/python"
            )
            subprocess.Popen(
                [venv_python, "sync_vault.py", "--file", path],
                cwd=os.path.expanduser("~/Pandora/brain")
            )
            # Trigger immediate git push
            threading.Timer(5.0, auto_git_push).start()


def run_module_job(module_id: str, tool: str,
                   params: dict = {}):
    if not os.path.exists(REGISTRY_PATH):
        return
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    module = registry.get("modules", {}).get(module_id, {})
    if not module.get("enabled", False):
        return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", MCP_PORT))
        request = json.dumps({
            "tool": "brain_tool",
            "params": {
                "action": "run",
                "module": module_id,
                "tool": tool,
                "params": params
            }
        }) + "\n"
        s.sendall(request.encode())
        response = s.recv(4096)
        s.close()
        result = json.loads(response.decode())
        log_metrics(
            f"scheduled_job | module:{module_id} "
            f"tool:{tool} status:complete"
        )
        print(f"Job {module_id}/{tool}: {result}")
    except Exception as e:
        log_metrics(
            f"scheduled_job | module:{module_id} "
            f"tool:{tool} status:error error:{e}"
        )


def auto_git_push():
    """Auto-commit and push vault changes to GitHub."""
    import subprocess
    try:
        vault_path = os.path.expanduser("~/Pandora")
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=vault_path,
            capture_output=True, text=True
        )
        if result.stdout.strip():
            subprocess.run(
                ["git", "add", "vault/"],
                cwd=vault_path
            )
            from datetime import datetime
            msg = f"Pandora auto-sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=vault_path
            )
            subprocess.run(
                ["git", "push"],
                cwd=vault_path
            )
            log_metrics("auto_git_push | vault synced to GitHub")
            print("Auto-pushed to GitHub")
        else:
            print("No vault changes to push")
    except Exception as e:
        print(f"Auto-push error: {e}")


def setup_schedule():
    schedule.every().hour.do(
        run_module_job, "tiered-memory",
        "run_tier_promotion_demotion"
    )
    schedule.every(5).minutes.do(
        run_module_job, "subconscious",
        "run_burst_adaptive"
    )
    schedule.every().day.at("02:00").do(
        run_module_job, "temporal-decay", "apply"
    )
    schedule.every().day.at("02:30").do(
        run_module_job, "stigmergic-memory", "evaporate"
    )
    schedule.every().day.at("03:00").do(
        run_module_job, "entity-resolution",
        "find_and_merge_entities"
    )
    schedule.every().sunday.at("03:00").do(
        run_module_job, "tda-gap-detection", "run"
    )
    schedule.every().sunday.at("03:30").do(
        run_module_job, "active-learning", "rank"
    )
    schedule.every().sunday.at("04:00").do(
        run_module_job, "schema-abstraction", "detect"
    )
    schedule.every().sunday.at("04:30").do(
        run_module_job, "mdl-pruning", "analyze"
    )
    schedule.every(7).days.do(
        run_module_job, "causal-discovery", "discover"
    )
    schedule.every(10).minutes.do(auto_git_push)
    schedule.every(14).days.do(
        run_module_job, "self-state", "generate"
    )


def main():
    print("Starting Pandora daemon...")
    print(f"Vault: {VAULT_PATH}")

    setup_schedule()

    observer = Observer()
    observer.schedule(
        DebouncedVaultWatcher(),
        VAULT_PATH,
        recursive=True
    )
    observer.start()
    print("Watching vault for changes...")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Daemon stopping...")
        observer.stop()
    observer.join()
    print("Daemon stopped")


if __name__ == "__main__":
    main()
