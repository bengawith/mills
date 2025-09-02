
# ---
# WebSocket Connection Manager for real-time updates.
# Handles client connections, event broadcasting, subscription management, and connection lifecycle.
# Used for pushing live updates to frontend clients.
# ---

import json
import logging
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and handles event broadcasting.
    Tracks active connections, subscriptions, and client metadata.
    Provides methods for connecting, disconnecting, sending, and broadcasting events.
    """
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        # Store connections by subscription type
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "maintenance": set(),
            "machines": set(),
            "production": set(),
            "all": set()
        }
        # Store client metadata
        self.client_info: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Accept a new WebSocket connection, store metadata, and subscribe to 'all' by default.
        Sends a welcome message to the client.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        # Store client info
        self.client_info[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "subscriptions": set()
        }
        # Subscribe to 'all' by default
        self.subscriptions["all"].add(websocket)
        self.client_info[websocket]["subscriptions"].add("all")
        logger.info(f"WebSocket client connected: {client_id or 'unknown'}")
        # Send welcome message
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "message": "Connected to Mill Dash WebSocket",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection and clean up subscriptions and metadata.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # Remove from all subscriptions
        for subscription_set in self.subscriptions.values():
            subscription_set.discard(websocket)
            
        # Remove client info
        client_info = self.client_info.pop(websocket, {})
        client_id = client_info.get("client_id", "unknown")
        
        logger.info(f"WebSocket client disconnected: {client_id}")
        

    async def send_personal_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """
        Send a message to a specific client via WebSocket.
        """
        try:
            message = json.dumps(data, default=str)
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            

    async def broadcast_to_subscription(self, subscription_type: str, data: Dict[str, Any]):
        """
        Broadcast a message to all clients subscribed to a specific event type.
        Cleans up disconnected clients after broadcasting.
        """
        if subscription_type not in self.subscriptions:
            logger.warning(f"Unknown subscription type: {subscription_type}")
            return
        connections = self.subscriptions[subscription_type].copy()
        if not connections:
            logger.debug(f"No clients subscribed to {subscription_type}")
            return
        message = json.dumps(data, default=str)
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
        logger.debug(f"Broadcasted to {len(connections) - len(disconnected)} clients in {subscription_type}")
        

    async def broadcast_to_all(self, data: Dict[str, Any]):
        """
        Broadcast a message to all connected clients (subscribed to 'all').
        """
        await self.broadcast_to_subscription("all", data)
        

    async def subscribe(self, websocket: WebSocket, subscription_types: List[str]):
        """
        Subscribe a client to specific event types (e.g., dashboard, maintenance).
        Updates client metadata and sends confirmation.
        """
        if websocket not in self.client_info:
            logger.warning("Attempted to subscribe unknown client")
            return
        for sub_type in subscription_types:
            if sub_type in self.subscriptions:
                self.subscriptions[sub_type].add(websocket)
                self.client_info[websocket]["subscriptions"].add(sub_type)
                logger.debug(f"Client subscribed to {sub_type}")
            else:
                logger.warning(f"Unknown subscription type: {sub_type}")
        # Send confirmation
        await self.send_personal_message(websocket, {
            "type": "subscription_confirmed",
            "subscriptions": list(self.client_info[websocket]["subscriptions"]),
            "timestamp": datetime.utcnow().isoformat()
        })
        

    async def unsubscribe(self, websocket: WebSocket, subscription_types: List[str]):
        """
        Unsubscribe a client from specific event types.
        Updates client metadata and sends confirmation.
        """
        if websocket not in self.client_info:
            return
        for sub_type in subscription_types:
            self.subscriptions.get(sub_type, set()).discard(websocket)
            self.client_info[websocket]["subscriptions"].discard(sub_type)
        # Send confirmation
        await self.send_personal_message(websocket, {
            "type": "unsubscription_confirmed", 
            "subscriptions": list(self.client_info[websocket]["subscriptions"]),
            "timestamp": datetime.utcnow().isoformat()
        })
        

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current connections, subscriptions, and clients.
        Useful for monitoring and debugging WebSocket usage.
        """
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                sub_type: len(connections) 
                for sub_type, connections in self.subscriptions.items()
            },
            "clients": [
                {
                    "client_id": info.get("client_id"),
                    "connected_at": info.get("connected_at"),
                    "subscriptions": list(info.get("subscriptions", set()))
                }
                for info in self.client_info.values()
            ]
        }


# Global connection manager instance for use throughout the backend
manager = ConnectionManager()


# Event types for different data streams
class EventTypes:
    """
    Constants for different event types that can be broadcast to clients.
    Used for type-safe event handling in the backend and frontend.
    """
    MACHINE_STATUS_UPDATE = "machine_status_update"
    MAINTENANCE_ALERT = "maintenance_alert"
    PRODUCTION_METRIC_UPDATE = "production_metric_update"
    DASHBOARD_REFRESH = "dashboard_refresh"
    TICKET_STATUS_CHANGE = "ticket_status_change"
    TICKET_CREATED = "ticket_created"
    SYSTEM_ALERT = "system_alert"
    HEARTBEAT = "heartbeat"


# Utility function to broadcast events with proper formatting
async def broadcast_event(event_type: str, data: Dict[str, Any], subscription_filter: Optional[str] = None):
    """
    Broadcasts an event to clients, formatting the message and filtering by subscription type if provided.
    Args:
        event_type: Type of event (from EventTypes)
        data: Event data payload
        subscription_filter: Optional subscription type to filter recipients
    """
    event_message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    if subscription_filter:
        await manager.broadcast_to_subscription(subscription_filter, event_message)
    else:
        await manager.broadcast_to_all(event_message)
    logger.debug(f"Broadcasted event: {event_type} to {subscription_filter or 'all'}")
