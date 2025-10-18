import json

import websockets

from ..utils.loadConfig import load_config
from neuro_api.trio_ws import TrioNeuroAPI  # or whichever class your version uses
from neuro_api.command import Action  # and other command helpers

cfg = load_config()
HOST = cfg.get("host", "127.0.0.1")
PORT = int(cfg.get("port", 8765))
AUTH_TOKEN = cfg.get("auth_token", "replace-with-a-strong-secret")

# -------- Neurosama / Neuro-API integration --------

class NeuroClient(TrioNeuroAPI):
    """
    Subclassing the SDK’s WebSocket client, handling incoming action requests from Neuro,
    then forwarding them to Windows via your WebSocket interface.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(game_title="Windows", *args, **kwargs)
        # You can store additional state here

    async def handle_action(self, action: Action):
        """
        This is called by the SDK when Neuro-sama requests an action.
        e.g. action.name might be "move", "click", etc.
        action.data is a dict of parameters.
        """
        name = action.name
        params = action.data or {}
        print(f"[NEURO] Received action: {name}, params: {params}")

        # Forward to Windows API via WebSocket
        uri = f"ws://{HOST}:{PORT}"
        async with websockets.connect(uri) as ws:
            msg = {
                "token": AUTH_TOKEN,
                "action": name,
                **params,
            }
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            print(f"[WINRESP] {resp}")

            # Optionally, send back an “action result” to Neuro-sama
            # using the SDK’s method. e.g.:
            return self.send_action_result(action.id, resp)

    async def on_connect(self):
        print("[NEURO] Connected to Neuro API")

    async def on_disconnect(self):
        print("[NEURO] Disconnected from Neuro API")

async def neuro_client():
    client = NeuroClient()
    client.connect()
