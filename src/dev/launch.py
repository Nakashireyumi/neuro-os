# src/dev/launch.py
import sys
import subprocess
import yaml
from pathlib import Path
import importlib
import traceback
import os

def load_package_map(path=Path("src/global/packages.yaml")):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("packages", {}).get("python", {})

def main():
    package_map = load_package_map()
    if not package_map:
        print("No packages found in YAML.")
        sys.exit(1)

    env = dict(os.environ)
    # Ensure src/ is on PYTHONPATH
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[3]) + os.pathsep + env.get("PYTHONPATH", "")

    processes = []
    for name, module in package_map.items():
        print(f"Starting {name} -> {module}")
        try:
            # Try to import to validate
            importlib.import_module(module)
        except Exception as e:
            print(f"[IMPORT ERROR] Could not import {module}: {e}")
            print(traceback.format_exc())
            continue

        try:
            cmd = [sys.executable, "-m", module]
            proc = subprocess.Popen([sys.executable, "-m", module], env=env)
            processes.append((name, proc))
        except Exception as e:
            print(f"[LAUNCH ERROR] Could not start {module}: {e}")
            print(traceback.format_exc())

    # Wait for all to finish
    for name, proc in processes:
        proc.wait()
        print(f"{name} exited with code {proc.returncode}")

if __name__ == "__main__":
    main()