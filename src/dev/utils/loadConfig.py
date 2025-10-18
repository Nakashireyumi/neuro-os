from pathlib import Path
import yaml

# ------------------------------------------
# CONFIGURATION
# ------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
WINDOWS_API = ROOT / "windows-api"
CONFIG_PATH = WINDOWS_API / "src" / "resources" / "gui" / "config" / "authentication.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing authentication config at: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
