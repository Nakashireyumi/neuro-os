# src/dev/launch.py
import sys
import subprocess
import yaml
from pathlib import Path
import importlib
import traceback
import os
import linecache
import inspect
import time
from datetime import datetime

print("PID:", os.getpid())

# Import configuration loader
from .utils.config_loader import get_config_loader, apply_trace_config

# Load configuration
config_loader = get_config_loader()
PROJECT_ROOT = Path(__file__).parents[2].resolve()

# Get trace configuration from config file
trace_config = config_loader.get_trace_config()
USE_COLOR = trace_config.get("use_color", True)
SHOW_FILE_PATH = trace_config.get("show_file_path", False)
SHOW_TIMESTAMP = trace_config.get("show_timestamp", True)
MAX_VALUE_LEN = trace_config.get("max_value_len", 60)
MAX_LOCALS = trace_config.get("max_locals", 4)
MAX_STACK_DEPTH = trace_config.get("max_stack_depth", 12)
TRACE_INCLUDE = trace_config.get("include_paths", ["src/dev"])
TRACE_EXCLUDE_FUNCS = set(trace_config.get("exclude_functions", ["write_log", "trace"]))
TRACE_EVENTS = set(trace_config.get("events", ["call", "return", "exception"]))

# Set log path from config or default
log_config = config_loader.get_logging_config()
LOG_PATH = Path(log_config.get("file", "logs/neuro_os_trace.log"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

start_time = time.perf_counter()

# === COLOR UTILITIES ===
def color(txt, fg=None, style=None):
    if not USE_COLOR:
        return txt
    codes = {
        "reset": "\033[0m", "bold": "\033[1m",
        "gray": "\033[90m", "red": "\033[91m",
        "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    return f"{codes.get(style, '')}{codes.get(fg, '')}{txt}{codes['reset']}"

# === FORMATTING HELPERS ===
def short(v):
    s = repr(v)
    return s if len(s) <= MAX_VALUE_LEN else s[:MAX_VALUE_LEN - 3] + "..."

def now():
    return f"{(time.perf_counter() - start_time):6.3f}s"

def fmt_path(rel, lineno):
    if SHOW_FILE_PATH:
        return f"{rel}:{lineno}"
    return f"{rel.name}:{lineno}"

def fmt_locals(locals_dict):
    items = [
        f"{color(k, 'blue')}={color(short(v), 'gray')}"
        for k, v in locals_dict.items()
        if not k.startswith("__") and not inspect.isfunction(v)
    ]
    return ", ".join(items[:MAX_LOCALS])

def write_log(line):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# === MAIN TRACER ===
def trace(frame, event, arg):
    if not config_loader.is_trace_enabled():
        return  # Tracing disabled
    
    filename = Path(frame.f_code.co_filename).resolve()
    try:
        filename.relative_to(PROJECT_ROOT)
    except ValueError:
        return  # Skip non-project files

    rel = filename.relative_to(PROJECT_ROOT)
    rel_posix = rel.as_posix()
    
    # Check include paths
    if TRACE_INCLUDE and not any(p in rel_posix for p in TRACE_INCLUDE):
        return
    
    func = frame.f_code.co_name
    
    # Check excluded functions
    if func in TRACE_EXCLUDE_FUNCS:
        return
    
    # Check events
    if event not in TRACE_EVENTS:
        return
    
    depth = len(inspect.stack(0)) - 1
    indent = "│  " * (depth % MAX_STACK_DEPTH)
    ts = f"[{now()}]" if SHOW_TIMESTAMP else ""

    def log(msg):
        print(msg)
        write_log(msg)

    # === CALL ===
    if event == "call":
        args, _, _, values = inspect.getargvalues(frame)
        arg_str = ", ".join(f"{a}={short(values[a])}" for a in args if a in values)
        header = f"\n{indent}{color('╭▶', 'cyan', 'bold')} {color(func, 'green', 'bold')}() {color(fmt_path(rel, frame.f_lineno), 'gray')} {ts}"
        log(header)
        if arg_str:
            log(f"{indent}{color('│ args:', 'yellow')} {arg_str}")

    # === LINE ===
    elif event == "line":
        line = linecache.getline(str(filename), frame.f_lineno).strip()
        log(f"{indent}{color('│ →', 'cyan')} {color(line, 'reset')}")
        local_vars = fmt_locals(frame.f_locals)
        if local_vars:
            log(f"{indent}{color('│ • locals:', 'gray')} {local_vars}")

    # === RETURN ===
    elif event == "return":
        msg = f"{indent}{color('╰↩', 'green', 'bold')} {color('return', 'gray')} {short(arg)} {ts}"
        log(msg)

    # === EXCEPTION ===
    elif event == "exception":
        exc_type, exc_value, _ = arg
        msg = f"{indent}{color('💥', 'red', 'bold')} {exc_type.__name__}: {exc_value}  {color(fmt_path(rel, frame.f_lineno), 'gray')}"
        log(msg)

    return trace

# Apply trace configuration
apply_trace_config(trace)
if config_loader.is_trace_enabled():
    print(color(f"🧠 SmartTrace enabled", "magenta", "bold"))
else:
    print(color(f"🧠 SmartTrace disabled by configuration", "yellow", "bold"))

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