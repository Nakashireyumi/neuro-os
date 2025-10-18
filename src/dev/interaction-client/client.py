import websockets
import json

from ..utils.loadConfig import load_config

cfg = load_config
HOST = cfg.get("host", "127.0.0.1")
PORT = int(cfg.get("port", 8765))
AUTH_TOKEN = cfg.get("auth_token", "replace-with-a-strong-secret")

class WindowsAPIClient:
    async def send_message(name, **params):
        uri = f"ws://{HOST}:{PORT}"
        async with websockets.connect(uri) as ws:
            msg = {
                "token": AUTH_TOKEN,
                "action": name,
                **params,
            }
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            return resp;