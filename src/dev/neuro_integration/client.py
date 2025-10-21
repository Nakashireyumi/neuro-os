import json

import websockets

from ..utils.loadConfig import load_config
from neuro_api.api import AbstractNeuroAPI, NeuroAction
from neuro_api.command import *
from . import load_actions

cfg = load_config()
HOST = cfg.get("host", "127.0.0.1")
PORT = int(cfg.get("port", 8766))
AUTH_TOKEN = cfg.get("auth_token", "replace-with-a-strong-secret")

# -------- Neurosama / Neuro-API integration --------

class NeuroClient(AbstractNeuroAPI):
    """
    Subclassing the SDK’s WebSocket client, handling incoming action requests from Neuro,
    then forwarding them to Windows via your WebSocket interface.
    """
    def __init__(self, websocket):
        self.websocket = websocket
        self.name = "windows-user"
        super().__init__(self.name)

    async def write_to_websocket(self, data: str) -> None:
        await self.websocket.send(data)

    async def read_from_websocket(self) -> str:
        return await self.websocket.recv()

    async def initialize(self):
        # Send startup command
        await self.send_startup_command()

        # Register actions
        actions = load_actions()

        await self.register_actions(actions)

    async def handle_action(self, action: NeuroAction):
        """
        This is called by the SDK when Neuro-sama requests an action.
        e.g. action.name might be "move", "click", etc.
        action.data is a dict of parameters.
        """
        name = action.name
        params = json.loads(action.data) or {}
        print(f"[NEURO] Received action: {name}, params: {params}")

        # Handle Neuro-OS internal actions locally (do not forward to Windows API)
        if name == "context_update":
            # Accept and log context for diagnostics; treat as no-op for Windows API
            result = {
                "status": "ok",
                "result": {
                    "message": "context_update received by neuro-os",
                    "summary_len": len(params.get("context_summary", ""))
                }
            }
            await self.send_action_result(action.id_, json.dumps(result))
            return

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
            await self.send_action_result(action.id_, resp)

    async def on_connect(self):
        print("[NEURO] Connected to Neuro API")

    async def on_disconnect(self):
        print("[NEURO] Disconnected from Neuro API")

async def neuro_client():
    uri = f"ws://127.0.0.1:8000"
    async with websockets.connect(uri) as websocket:
        client = NeuroClient(websocket)
        await client.initialize()

        # Read messages in a loop
        while True:
            try:
                await client.read_message()
            except websockets.exceptions.ConnectionClosed:
                break
