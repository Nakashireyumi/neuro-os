import os
from pathlib import Path
import psutil
import subprocess
import signal
import sys
import socket

ROOT = Path(__file__).resolve().parents[3]
WINDOWS_API = ROOT / "windows-api"

# ------------------------------------------
# SERVER MANAGEMENT
# ------------------------------------------
server_proc = None

def _is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            return s.connect_ex((host, port)) == 0
        except OSError:
            return False

def _read_windows_api_port(default: int = 8766) -> int:
    cfg_path = WINDOWS_API / "src" / "resources" / "gui" / "config" / "authentication.yaml"
    try:
        text = cfg_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("port:"):
                return int(line.split(":", 1)[1].strip().strip('"'))
    except Exception:
        pass
    return default


def start_windows_api_server():
    global server_proc

    env = os.environ.copy()
    src_path = str(WINDOWS_API / "src")

    # Ensure Python can locate all nested packages
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

    # Port guard: skip starting if already bound
    host = "127.0.0.1"
    port = _read_windows_api_port()
    if _is_port_in_use(host, port):
        print(f"[LAUNCH] Windows interactions server already running on ws://{host}:{port}; skipping spawn")
        return None

    # Launch the Windows API interactions server module directly
    print("[LAUNCH] Starting Windows interactions server (module dev.cassitly.python.interactions-api)...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "dev.cassitly.python.interactions-api"],
        cwd=WINDOWS_API / "src",
        env=env
    )
    return server_proc

def stop_windows_api_server():
    global server_proc
    if server_proc:
        print("[STOP] Terminating Windows API server...")
        psutil.Process(server_proc.pid).send_signal(signal.CTRL_BREAK_EVENT)
        server_proc.wait(timeout=5)
        print("[STOP] Server stopped.")
        server_proc = None