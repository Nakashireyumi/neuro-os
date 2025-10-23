"""
Dual Connection Manager for neuro-os
Manages connections to both intermediary (monitoring) and backend (Neuro API)
"""

import asyncio
import json
import logging
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class RelayConnectionManager:
    """Manages dual connections to intermediary and backend"""
    
    def __init__(self, 
                 intermediary_url: str = "ws://127.0.0.1:8765",
                 backend_url: str = "ws://127.0.0.1:8000",
                 auth_token: Optional[str] = None):
        self.intermediary_url = intermediary_url
        self.backend_url = backend_url
        self.auth_token = auth_token
        
        # Connection state
        self.intermediary_ws = None
        self.backend_ws = None
        self.registered = {"intermediary": False, "backend": False}
        
        # Stats tracking
        self.stats = {
            "intermediary": {"connected": False, "messages_sent": 0, "messages_received": 0},
            "backend": {"connected": False, "messages_sent": 0, "messages_received": 0},
            "last_update": None
        }
        
        # Callbacks
        self.on_intermediary_message: Optional[Callable] = None
        self.on_backend_message: Optional[Callable] = None
    
    async def connect_all(self):
        """Connect to both intermediary and backend"""
        logger.info(f"Connecting to intermediary at {self.intermediary_url}")
        logger.info(f"Connecting to backend at {self.backend_url}")
        
        # Connect concurrently
        try:
            results = await asyncio.gather(
                self._connect_intermediary(),
                self._connect_backend(),
                return_exceptions=True
            )
            
            # Check for errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    conn_type = ["intermediary", "backend"][i]
                    logger.error(f"Failed to connect to {conn_type}: {result}")
            
            logger.info(f"Connection status - Intermediary: {self.registered['intermediary']}, Backend: {self.registered['backend']}")
            
        except Exception as e:
            logger.error(f"Error during connection: {e}")
    
    async def _connect_intermediary(self):
        """Connect to intermediary as watcher"""
        try:
            import websockets
            
            self.intermediary_ws = await websockets.connect(self.intermediary_url)
            self.stats["intermediary"]["connected"] = True
            logger.info("Connected to intermediary")
            
            # Register as watcher
            register_msg = {
                "type": "register",
                "client_type": "watcher",
                "client_id": "neuro-os-client",
                "auth_token": self.auth_token
            }
            
            await self.intermediary_ws.send(json.dumps(register_msg))
            self.stats["intermediary"]["messages_sent"] += 1
            
            # Wait for registration confirmation
            response = await self.intermediary_ws.recv()
            self.stats["intermediary"]["messages_received"] += 1
            
            resp_data = json.loads(response)
            if resp_data.get("type") == "registered":
                self.registered["intermediary"] = True
                logger.info("Registered with intermediary as watcher")
            else:
                logger.warning(f"Unexpected registration response: {resp_data}")
            
        except ImportError:
            logger.error("websockets library not installed. Install with: pip install websockets")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to intermediary: {e}")
            self.stats["intermediary"]["connected"] = False
            raise
    
    async def _connect_backend(self):
        """Connect to backend for Neuro API integration"""
        try:
            import websockets
            
            # Note: This connection is typically managed by the NeuroClient
            # This is just for monitoring/stats
            self.backend_ws = await websockets.connect(self.backend_url)
            self.stats["backend"]["connected"] = True
            self.registered["backend"] = True
            logger.info("Connected to backend")
            
        except ImportError:
            logger.error("websockets library not installed. Install with: pip install websockets")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to backend: {e}")
            self.stats["backend"]["connected"] = False
            raise
    
    async def send_to_intermediary(self, message: dict) -> bool:
        """Send message to intermediary"""
        if not self.intermediary_ws or not self.registered["intermediary"]:
            logger.warning("Not connected to intermediary")
            return False
        
        try:
            await self.intermediary_ws.send(json.dumps(message))
            self.stats["intermediary"]["messages_sent"] += 1
            self.stats["last_update"] = datetime.now().isoformat()
            return True
        except Exception as e:
            logger.error(f"Failed to send to intermediary: {e}")
            return False
    
    async def send_to_backend(self, message: dict) -> bool:
        """Send message to backend"""
        if not self.backend_ws or not self.registered["backend"]:
            logger.warning("Not connected to backend")
            return False
        
        try:
            await self.backend_ws.send(json.dumps(message))
            self.stats["backend"]["messages_sent"] += 1
            self.stats["last_update"] = datetime.now().isoformat()
            return True
        except Exception as e:
            logger.error(f"Failed to send to backend: {e}")
            return False
    
    async def monitor_intermediary(self):
        """Monitor messages from intermediary"""
        if not self.intermediary_ws:
            logger.warning("Not connected to intermediary for monitoring")
            return
        
        try:
            async for message in self.intermediary_ws:
                self.stats["intermediary"]["messages_received"] += 1
                
                try:
                    data = json.loads(message)
                    
                    # Call callback if set
                    if self.on_intermediary_message:
                        await self.on_intermediary_message(data)
                    else:
                        logger.debug(f"Intermediary message: {data.get('type', 'unknown')}")
                
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from intermediary: {message[:100]}")
        
        except Exception as e:
            logger.error(f"Error monitoring intermediary: {e}")
            self.stats["intermediary"]["connected"] = False
    
    async def monitor_backend(self):
        """Monitor messages from backend (optional, usually handled by NeuroClient)"""
        if not self.backend_ws:
            logger.warning("Not connected to backend for monitoring")
            return
        
        try:
            async for message in self.backend_ws:
                self.stats["backend"]["messages_received"] += 1
                
                try:
                    data = json.loads(message)
                    
                    # Call callback if set
                    if self.on_backend_message:
                        await self.on_backend_message(data)
                    else:
                        logger.debug(f"Backend message: {data.get('type', 'unknown')}")
                
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from backend: {message[:100]}")
        
        except Exception as e:
            logger.error(f"Error monitoring backend: {e}")
            self.stats["backend"]["connected"] = False
    
    async def close_all(self):
        """Close all connections"""
        logger.info("Closing all relay connections")
        
        if self.intermediary_ws:
            try:
                await self.intermediary_ws.close()
            except Exception as e:
                logger.error(f"Error closing intermediary connection: {e}")
        
        if self.backend_ws:
            try:
                await self.backend_ws.close()
            except Exception as e:
                logger.error(f"Error closing backend connection: {e}")
        
        self.stats["intermediary"]["connected"] = False
        self.stats["backend"]["connected"] = False
        self.registered = {"intermediary": False, "backend": False}
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            **self.stats,
            "registered": self.registered
        }
    
    def is_connected(self, connection_type: Optional[str] = None) -> bool:
        """Check if connections are active"""
        if connection_type == "intermediary":
            return self.stats["intermediary"]["connected"] and self.registered["intermediary"]
        elif connection_type == "backend":
            return self.stats["backend"]["connected"] and self.registered["backend"]
        else:
            # Both must be connected
            return (self.stats["intermediary"]["connected"] and 
                   self.stats["backend"]["connected"] and
                   self.registered["intermediary"] and 
                   self.registered["backend"])
