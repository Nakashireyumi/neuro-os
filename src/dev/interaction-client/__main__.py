"""
NEURO-OS Interaction Client
Uses Nakashireyumi/windows-api to control a Windows PC through a WebSocket interface.

This client automatically launches the Windows interactions API server,
connects to it, and sends actions like mouse/keyboard control for "Neurosama".
"""

import trio

from .client import neuro_client
from ..utils.winapi_management import start_windows_api_server, stop_windows_api_server

# ------------------------------------------
# ENTRY POINT
# ------------------------------------------
if __name__ == "__main__":
    try:
        start_windows_api_server()
        trio.run(neuro_client)
    except [KeyboardInterrupt, Exception]:
        print(Exception)
        print("\n[INTERRUPTED] Shutting down...")
    finally:
        stop_windows_api_server()
