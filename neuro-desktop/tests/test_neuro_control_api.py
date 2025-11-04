import json
from pathlib import Path
import pytest

def _patch_neuro_cfg_path(monkeypatch, tmp_path):
    """
    Allows the API to read/write a temp YAML path instead of the repo path.
    Only works if dashboard has a helper accessor. If not, comment this out
    and let it write to the default path in your local run.
    """
    try:
        import src.admin.dashboard as dash
    except Exception:
        return False

    # Fallback: monkeypatch functions if present; otherwise return False.
    for name in ("load_neuro_control_config", "save_neuro_control_config"):
        if not hasattr(dash, name):
            return False

    cfg_path = tmp_path / "resources" / "neuro_control.yaml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    # Wrap existing load/save to use the temp path
    def load_wrap():
        import yaml
        if cfg_path.exists():
            return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        return {"enabled": False, "theme": "Dark", "autostart": False, "allowed_actions": []}

    def save_wrap(data):
        import yaml
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    monkeypatch.setattr(dash, "load_neuro_control_config", load_wrap, raising=False)
    monkeypatch.setattr(dash, "save_neuro_control_config", save_wrap, raising=False)
    return True

@pytest.mark.usefixtures("flask_app")
def test_neuro_control_get(flask_app):
    client = flask_app.test_client()
    # Skip if route doesn’t exist in current branch
    if not any(str(r).startswith("/api/neuro-control") for r in flask_app.url_map.iter_rules()):
        pytest.skip("neuro-control API not present in this branch")
    r = client.get("/api/neuro-control")
    assert r.status_code == 200
    data = r.get_json()
    assert "enabled" in data

def test_neuro_control_save_and_get(flask_app, monkeypatch, tmp_path):
    client = flask_app.test_client()
    if not any(str(r).startswith("/api/neuro-control") for r in flask_app.url_map.iter_rules()):
        pytest.skip("neuro-control API not present in this branch")

    _patch_neuro_cfg_path(monkeypatch, tmp_path)

    payload = {"enabled": False, "theme": "Dark", "autostart": False, "allowed_actions": ["open_app"]}
    r = client.post("/api/neuro-control", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 200
    assert r.get_json().get("success", True)  # some branches may return raw object

    r2 = client.get("/api/neuro-control")
    data2 = r2.get_json()
    assert data2.get("theme") in ("Dark", "dark")
    assert isinstance(data2.get("allowed_actions", []), list)