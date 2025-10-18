"""
NEURO-OS Interaction Client
Uses Nakashireyumi/windows-api to control a Windows PC through a WebSocket interface.

This client automatically launches the Windows interactions API server,
connects to it, and sends actions like mouse/keyboard control for "Neurosama".
"""

import asyncio

from ..neuro_integration.client import neuro_client
from .client import WindowsAPIClient

# ------------------------------------------
# ENTRY POINT
# ------------------------------------------
if __name__ == "__main__":
    asyncio.run(neuro_client())