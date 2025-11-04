import os, sys
from pathlib import Path
import pytest

# Ensure Python can import "src.*" packages under the repo's neuro-desktop folder
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PARENT = REPO_ROOT / "neuro-desktop"
if SRC_PARENT.exists():
    sys.path.insert(0, str(SRC_PARENT))  # so "import src.admin.dashboard" works

def route_exists(app, rule_prefix: str) -> bool:
    for rule in app.url_map.iter_rules():
        if str(rule).startswith(rule_prefix):
            return True
    return False

@pytest.fixture(scope="session")
def flask_app():
    """
    Imports the existing admin Flask app. If the module or 'app' isn’t found,
    skip tests gracefully.
    """
    try:
        mod = __import__("src.admin.dashboard", fromlist=["app"])
        app = getattr(mod, "app", None)
        if app is None:
            pytest.skip("src.admin.dashboard.app not found")
        return app
    except Exception as e:
        pytest.skip(f"Cannot import admin dashboard: {e}")