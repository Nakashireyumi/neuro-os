import os
from pathlib import Path
import psutil
import subprocess
import signal
import sys

ROOT = Path(__file__).resolve().parents[3]
WINDOWS_API = ROOT / "windows-api"

# ------------------------------------------
# SERVER MANAGEMENT
# ------------------------------------------
server_proc = None

def start_windows_api_server():
    global server_proc

    env = os.environ.copy()
    src_path = str(WINDOWS_API / "src")

    # Ensure Python can locate all nested packages
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

    # Create a launcher command that simulates "python -m ..."
    launch_code = (
        "import runpy, sys; "
        "sys.path.insert(0, r'{}'); "
        "runpy.run_module('contributions.cassitly.python.interactions-api', run_name='__main__')"
    ).format(src_path.replace("\\", "\\\\"))

    print("[LAUNCH] Starting Windows interactions server (with module context)...")
    server_proc = subprocess.Popen(
        [sys.executable, "-c", launch_code],
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