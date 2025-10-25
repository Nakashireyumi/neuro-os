import json
import asyncio
from datetime import datetime

import websockets

from ..utils.loadConfig import load_config
from neuro_api.api import AbstractNeuroAPI, NeuroAction
from neuro_api.command import *
from . import load_actions

# Regionalization context provider
try:
    from src.regionalization.core import RegionalizationCore
except Exception:
    RegionalizationCore = None

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
        self._context_task = None
        self._reg = RegionalizationCore() if RegionalizationCore else None
        self._action_in_progress = False
        self._actions_registered = False
        self._pending_actions = None
        
        # Cache full context data for pagination
        self._cached_context = {
            'ocr_elements': [],
            'windows': [],
            'state': None,
            'timestamp': None
        }
        
        super().__init__(self.name)

    async def write_to_websocket(self, data: str) -> None:
        await self.websocket.send(data)

    async def read_from_websocket(self) -> str:
        return await self.websocket.recv()

    async def initialize(self):
        # Send startup command with retry
        await self._send_startup_with_retry()

        # Register actions with retry
        actions = load_actions()
        await self._register_actions_with_retry(actions)

        # Send a one-time capability/context primer so Neuro understands this game
        try:
            action_names = [a.name for a in load_actions()]
            primer = (
                f"Neuro-OS Windows integration is active. I can control the Windows UI via actions: "
                f"{', '.join(action_names)}. "
                f"I will periodically send summaries of the current screen, focused window, and available UI targets."
            )
            await self.send_context(primer, silent=True)
        except Exception:
            pass

        # Start periodic context publishing to the Neuro backend (rich summaries)
        if self._reg and self._context_task is None:
            self._context_task = asyncio.create_task(self._publish_context_loop())

    async def handle_action(self, action: NeuroAction):
        """
        This is called by the SDK when Neuro-sama requests an action.
        e.g. action.name might be "move", "click", etc.
        action.data is a dict of parameters.
        """
        name = action.name
        # Safely parse params
        try:
            params = json.loads(action.data) if action.data else {}
        except Exception:
            params = {}
        print(f"[NEURO] Received action: {name}, params: {params}")

        # Handle pagination and context actions
        if name in ["get_more_text", "get_more_windows", "refresh_context", "context_update"]:
            success, message = await self._handle_context_action(name, params)
            await self.send_action_result(action.id_, success, message)
            return

        # Execute the Windows action and wait for actual result
        self._action_in_progress = True
        try:
            success, message = await self._execute_windows_action(name, params)
            await self.send_action_result(action.id_, success, message)
        except Exception as e:
            await self.send_action_result(action.id_, False, f"Error: {str(e)}")
        finally:
            # We are no longer blocking Neuro; allow context publishing again
            self._action_in_progress = False

    async def on_connect(self):
        print("[NEURO] Connected to Neuro API")
        # Try to register actions if they weren't registered successfully before
        if not self._actions_registered and self._pending_actions:
            print("[NEURO] Attempting to register pending actions...")
            try:
                await self.register_actions(self._pending_actions)
                self._actions_registered = True
                print(f"[NEURO] Successfully registered {len(self._pending_actions)} pending actions")
            except Exception as e:
                print(f"[NEURO] Failed to register pending actions: {e}")

    async def on_disconnect(self):
        print("[NEURO] Disconnected from Neuro API")
        self._actions_registered = False
    
    async def _send_startup_with_retry(self, max_retries: int = 5, retry_delay: float = 2.0):
        """Send startup command with retry logic for connection issues"""
        for attempt in range(max_retries):
            try:
                await self.send_startup_command()
                print(f"[NEURO] Startup command sent successfully")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[NEURO] Startup command failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"[NEURO] Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"[NEURO] Failed to send startup command after {max_retries} attempts: {e}")
                    raise
    
    async def _register_actions_with_retry(self, actions, max_retries: int = 5, retry_delay: float = 2.0):
        """Register actions with retry logic for connection issues"""
        self._pending_actions = actions  # Store for potential reregistration
        
        for attempt in range(max_retries):
            try:
                await self.register_actions(actions)
                print(f"[NEURO] Successfully registered {len(actions)} actions")
                self._actions_registered = True
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[NEURO] Action registration failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"[NEURO] Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"[NEURO] Failed to register actions after {max_retries} attempts: {e}")
                    print(f"[NEURO] Will continue listening for backend to become available...")
    
    async def _handle_context_action(self, name: str, params: dict) -> tuple[bool, str]:
        """Handle context pagination and refresh actions"""
        try:
            if name == "context_update":
                return True, "context_update received by neuro-os"
            
            if name == "get_more_text":
                return await self._get_more_text(params)
            
            if name == "get_more_windows":
                return await self._get_more_windows(params)
            
            if name == "refresh_context":
                return await self._refresh_context(params)
            
            return False, f"Unknown context action: {name}"
        
        except Exception as e:
            print(f"[CONTEXT_ACTION_ERR] {e}")
            import traceback
            traceback.print_exc()
            return False, f"Context action failed: {str(e)}"
    
    async def _get_more_text(self, params: dict) -> tuple[bool, str]:
        """Get paginated text/UI elements"""
        if not self._reg:
            return False, "Regionalization not available"
        
        offset = params.get('offset', 0)
        limit = params.get('limit', 50)
        filter_type = params.get('filter_type', 'all')
        
        # Get cached OCR elements
        ocr_elements = self._cached_context.get('ocr_elements', [])
        
        if not ocr_elements:
            return False, "No OCR data available. Wait for next context update."
        
        # Filter by type if requested
        if filter_type != 'all':
            filtered = [e for e in ocr_elements if e.element_type == filter_type]
        else:
            filtered = ocr_elements
        
        # Paginate
        paginated = filtered[offset:offset + limit]
        total = len(filtered)
        
        if not paginated:
            return True, f"No more items. Total available: {total}"
        
        # Format response
        lines = []
        lines.append(f"Text Items ({offset + 1}-{offset + len(paginated)} of {total}):")
        for elem in paginated:
            lines.append(f'  - [{elem.element_type}] "{elem.text}" at ({elem.center_x}, {elem.center_y})')
        
        if offset + len(paginated) < total:
            remaining = total - (offset + len(paginated))
            lines.append(f"\n... and {remaining} more items. Use get_more_text with offset={offset + limit} to see more.")
        
        return True, "\n".join(lines)
    
    async def _get_more_windows(self, params: dict) -> tuple[bool, str]:
        """Get paginated window list"""
        if not self._reg:
            return False, "Regionalization not available"
        
        offset = params.get('offset', 0)
        limit = params.get('limit', 20)
        include_minimized = params.get('include_minimized', False)
        
        # Get cached windows
        state = self._cached_context.get('state')
        if not state or not state.all_regions:
            return False, "No window data available. Wait for next context update."
        
        # Filter windows
        windows = [r for r in state.all_regions if r.region_type.value == 'window']
        
        # Paginate
        paginated = windows[offset:offset + limit]
        total = len(windows)
        
        if not paginated:
            return True, f"No more windows. Total available: {total}"
        
        # Format response
        lines = []
        lines.append(f"Windows ({offset + 1}-{offset + len(paginated)} of {total}):")
        for i, window in enumerate(paginated, start=offset + 1):
            center_x = window.bounds.x + window.bounds.width // 2
            center_y = window.bounds.y + window.bounds.height // 2
            is_focused = window.metadata.get('focused', False) if window.metadata else False
            focus_marker = " [FOCUSED]" if is_focused else ""
            title = window.title[:60] if window.title and len(window.title) > 60 else window.title
            lines.append(f"  {i}. {title}{focus_marker}")
            lines.append(f"     App: {window.application}, Position: ({window.bounds.x}, {window.bounds.y}), Size: {window.bounds.width}x{window.bounds.height}")
            lines.append(f"     Click center: ({center_x}, {center_y})")
        
        if offset + len(paginated) < total:
            remaining = total - (offset + len(paginated))
            lines.append(f"\n... and {remaining} more windows. Use get_more_windows with offset={offset + limit} to see more.")
        
        return True, "\n".join(lines)
    
    async def _refresh_context(self, params: dict) -> tuple[bool, str]:
        """Force context refresh with custom settings"""
        if not self._reg:
            return False, "Regionalization not available"
        
        detail_level = params.get('detail_level', 'standard')
        include_ocr = params.get('include_ocr', True)
        include_vision = params.get('include_vision', False)
        max_items = params.get('max_items_per_category', 15)
        
        try:
            # Force update regionalization
            await self._reg.force_update()
            state = self._reg.get_current_state()
            
            if not state:
                return False, "Unable to get current state"
            
            # Get context with custom settings
            ocr_elements = self._reg.get_ocr_elements() if include_ocr else []
            
            # Build context message based on detail level
            from src.types.neuro_types import NeuroMessageBuilder
            builder = NeuroMessageBuilder()
            builder.update_state(state)
            
            # For now, use standard context builder
            # TODO: Implement detail level variants
            context_msg = builder.build_context_message(ocr_elements if include_ocr else None, self._reg.ocr_detector if include_ocr else None)
            
            # Cache the data
            self._cached_context = {
                'ocr_elements': ocr_elements,
                'windows': [r for r in state.all_regions if r.region_type.value == 'window'],
                'state': state,
                'timestamp': datetime.now()
            }
            
            # Send as context update
            await self.send_context(context_msg, silent=True)
            
            return True, f"Context refreshed with {detail_level} detail level. {len(ocr_elements)} UI elements detected."
        
        except Exception as e:
            print(f"[REFRESH_ERR] {e}")
            import traceback
            traceback.print_exc()
            return False, f"Failed to refresh context: {str(e)}"

    async def _execute_windows_action(self, name: str, params: dict) -> tuple[bool, str]:
        """Execute a Windows action and return (success, message)."""
        try:
            # Fill defaults for click if coordinates are missing
            if name == "click" and ("x" not in params or "y" not in params):
                try:
                    import pyautogui
                    x, y = pyautogui.position()
                    params = {**params, "x": int(x), "y": int(y)}
                except Exception:
                    pass

            uri = f"ws://{HOST}:{PORT}"
            async with websockets.connect(uri) as ws:
                msg = {"token": AUTH_TOKEN, "action": name, **params}
                await ws.send(json.dumps(msg))
                resp_text = await ws.recv()
                print(f"[WINRESP] {resp_text}")
                
                # Parse response
                try:
                    resp = json.loads(resp_text)
                    if resp.get("status") == "ok":
                        result = resp.get("result", {})
                        return True, f"Action '{name}' completed: {json.dumps(result)}"
                    elif resp.get("status") == "error":
                        error = resp.get("error", {})
                        error_msg = error.get("message", "Unknown error")
                        return False, f"Action '{name}' failed: {error_msg}"
                    else:
                        return True, f"Action '{name}' completed with unknown status"
                except json.JSONDecodeError:
                    return True, f"Action '{name}' completed (response: {resp_text[:100]})"
                    
        except Exception as e:
            print(f"[WINERR] {e}")
            return False, f"Failed to execute action: {str(e)}"

    async def _publish_context_once(self):
        if not self._reg:
            print("[CONTEXT] Regionalization not available")
            return
        # Do not send context while Neuro is waiting for an action result
        if getattr(self, "_action_in_progress", False):
            print("[CONTEXT] Skipping - action in progress")
            return
        try:
            print("[CONTEXT] Updating regionalization state...")
            await self._reg.force_update()
            state = self._reg.get_current_state()
            if not state:
                print("[CONTEXT] No state available")
                return
            context_msg = self._reg.get_context_message()
            print(f"[CONTEXT] Sending context: {context_msg[:200]}...")
            # Use SDK "context" command (proper protocol) so backend accepts it
            await self.send_context(context_msg, silent=True)
            print("[CONTEXT] Context sent successfully")
        except Exception as e:
            print(f"[CONTEXT_ERR] Failed to publish context: {e}")
            import traceback
            traceback.print_exc()

    async def _publish_context_loop(self):
        print("[CONTEXT] Starting context publishing loop (2s check, send on change)")
        last_context_msg = None
        
        try:
            while True:
                # Check state more frequently but only send if changed
                if not self._reg:
                    await asyncio.sleep(5)
                    continue
                    
                if getattr(self, "_action_in_progress", False):
                    await asyncio.sleep(2)
                    continue
                    
                try:
                    await self._reg.force_update()
                    state = self._reg.get_current_state()
                    if not state:
                        await asyncio.sleep(2)
                        continue
                        
                    context_msg = self._reg.get_context_message()
                    
                    # Only send if context actually changed
                    if context_msg != last_context_msg:
                        print(f"[CONTEXT] State changed, sending update")
                        
                        # Cache data for pagination
                        ocr_elements = self._reg.get_ocr_elements()
                        self._cached_context = {
                            'ocr_elements': ocr_elements,
                            'windows': [r for r in state.all_regions if r.region_type.value == 'window'],
                            'state': state,
                            'timestamp': datetime.now()
                        }
                        
                        await self.send_context(context_msg, silent=True)
                        last_context_msg = context_msg
                        print(f"[CONTEXT] Context sent successfully (cached {len(ocr_elements)} OCR elements)")
                    else:
                        print("[CONTEXT] No change, skipping update")
                        
                except KeyboardInterrupt:
                    # Re-raise to exit gracefully
                    raise
                except asyncio.CancelledError:
                    # Task was cancelled, exit gracefully
                    print("[CONTEXT] Context loop cancelled, shutting down")
                    raise
                except Exception as e:
                    print(f"[CONTEXT_ERR] Failed to publish context: {e}")
                    import traceback
                    traceback.print_exc()
                    
                await asyncio.sleep(2)  # Check every 2 seconds
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("[CONTEXT] Context publishing loop stopped")
            # Clean shutdown
            return


async def neuro_client():
    # Load relay config to get backend port
    try:
        from ..utils.loadConfig import load_config
        cfg = load_config()
        # neuro-os connects to neuro-relay's nakurity-backend (port 8001), not the real backend (8000)
        backend_port = cfg.get('relay_connection', {}).get('backend_port', 8001)
        backend_host = cfg.get('relay_connection', {}).get('host', '127.0.0.1')
    except Exception as e:
        print(f"[NEURO_CLIENT] Warning: Could not load config, using defaults: {e}")
        backend_host = '127.0.0.1'
        backend_port = 8001
    
    uri = f"ws://{backend_host}:{backend_port}"
    print(f"[NEURO_CLIENT] Connecting to neuro-relay backend at {uri}")
    
    async with websockets.connect(uri) as websocket:
        client = NeuroClient(websocket)
        await client.initialize()

        # Read messages in a loop
        while True:
            try:
                await client.read_message()
            except websockets.exceptions.ConnectionClosed:
                break
