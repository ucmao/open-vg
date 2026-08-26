"""WebSocket connection manager for real-time notifications."""
from fastapi import WebSocket
from typing import Dict, List
import os

from ..utils.logger import logger


class ConnectionManager:
    """Manage WebSocket connections for users."""
    
    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
        *,
        subprotocol: str | None = None,
    ) -> bool:
        """
        Connect a user's WebSocket.
        
        Args:
            user_id: User ID
            websocket: WebSocket connection
        """
        max_connections = max(1, int(os.getenv("WEBSOCKET_MAX_CONNECTIONS_PER_USER", "5")))
        if len(self.active_connections.get(user_id, [])) >= max_connections:
            await websocket.close(code=1008, reason="Too many WebSocket connections")
            return False

        await websocket.accept(subprotocol=subprotocol)
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
        return True
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """
        Disconnect a user's WebSocket.
        
        Args:
            user_id: User ID
            websocket: WebSocket connection
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Remove user entry if no connections left
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_message(self, user_id: int, message: dict):
        """
        Send a message to all of a user's connections.
        
        Args:
            user_id: User ID
            message: Message dictionary to send
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return
        
        # Send to all user's connections
        dead_connections = []
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {str(e)}")
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for websocket in dead_connections:
            self.disconnect(user_id, websocket)
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected users.
        
        Args:
            message: Message dictionary to send
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_message(user_id, message)


# Global connection manager instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
