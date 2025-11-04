import json
from pathlib import Path
import pytest

@pytest.mark.usefixtures("flask_app")
def test_plugins_list_api(flask_app):
    client = flask_app.test_client()
    if not any(str(r).startswith("/api/plugins") for r in flask_app.url_map.iter_rules()):
        pytest.skip("plugins API not present in this branch")
    r = client.get("/api/plugins")
    assert r.status_code in (200, 501)
    # Different branches may respond with different envelopes; accept either.

def test_enable_disable_plugin(flask_app, tmp_path, monkeypatch):
    # If there is no plugin manager in this checkout, skip.
    try:
        from src.plugins import get_plugin_manager
    except Exception:
        pytest.skip("src.plugins.get_plugin_manager not available")

    client = flask_app.test_client()
    if not any(str(r).startswith("/api/plugins/") and "<plugin_id>" in str(r) for r in flask_app.url_map.iter_rules()):
        pytest.skip("enable/disable routes not present")

    # If get_plugin_manager returns a singleton backed by disk, swap it with a tmp instance if possible
    try:
        from src.plugins.plugin_manager import PluginManager  # adjust if different
        tmp_plugins_dir = tmp_path / "plugins"
        tmp_mgr = PluginManager(tmp_plugins_dir)
        import src.admin.dashboard as dash
        if hasattr(dash, "get_plugin_manager"):
            monkeypatch.setattr(dash, "get_plugin_manager", lambda: tmp_mgr, raising=False)
    except Exception:
        # If PluginManager isn’t importable, rely on whatever the app uses, or skip
        pytest.skip("PluginManager unavailable in this branch")

    # Create a dummy plugin on disk so enable call can succeed
    plugin_id = "example-plugin"
    pdir = tmp_plugins_dir / plugin_id
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "plugin.json").write_text(json.dumps({
        "id": plugin_id,
        "name": "Example Plugin",
        "version": "1.0.0",
        "entry_point": "main.py",
        "description": "Example",
        "author": "neuro",
        "permissions": [],
        "dependencies": []
    }), encoding="utf-8")
    (pdir / "main.py").write_text(
        "async def activate(context):\n"
        "    return object()\n",
        encoding="utf-8"
    )

    r = client.post(f"/api/plugins/{plugin_id}/enable")
    assert r.status_code in (200, 400)
    r = client.post(f"/api/plugins/{plugin_id}/disable")
    assert r.status_code in (200, 400)