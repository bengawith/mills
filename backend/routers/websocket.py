"""
WebSocket router for real-time communication.
Handles WebSocket connections and manages real-time data streams.
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from websocket_manager import manager, EventTypes, broadcast_event

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = Query(None)):
    """
    Main WebSocket endpoint for real-time communication.
    
    Query Parameters:
        client_id: Optional client identifier
    """
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": manager.client_info[websocket]["connected_at"].isoformat()
                })
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                await manager.send_personal_message(websocket, {
                    "type": "error", 
                    "message": "Internal server error",
                    "timestamp": manager.client_info[websocket]["connected_at"].isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def handle_client_message(websocket: WebSocket, message: dict):
    """
    Handle incoming messages from WebSocket clients.
    
    Args:
        websocket: The WebSocket connection
        message: Parsed JSON message from client
    """
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # Handle subscription requests
        subscriptions = message.get("subscriptions", [])
        await manager.subscribe(websocket, subscriptions)
        
    elif message_type == "unsubscribe":
        # Handle unsubscription requests
        subscriptions = message.get("subscriptions", [])
        await manager.unsubscribe(websocket, subscriptions)
        
    elif message_type == "ping":
        # Handle ping/pong for connection testing
        await manager.send_personal_message(websocket, {
            "type": "pong",
            "timestamp": message.get("timestamp")
        })
        
    elif message_type == "get_status":
        # Send current connection status
        stats = manager.get_connection_stats()
        await manager.send_personal_message(websocket, {
            "type": "status_response",
            "data": stats
        })
        
    else:
        # Unknown message type
        await manager.send_personal_message(websocket, {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })

# Additional endpoints for triggering events (for testing/admin)
@router.websocket("/ws/admin")  
async def admin_websocket(websocket: WebSocket):
    """
    Admin WebSocket endpoint for broadcasting test events.
    This endpoint allows administrators to trigger events for testing.
    """
    await manager.connect(websocket, "admin")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_admin_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling admin message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_admin_message(websocket: WebSocket, message: dict):
    """Handle admin messages for broadcasting events."""
    action = message.get("action")
    
    if action == "broadcast_test":
        # Broadcast a test event
        event_type = message.get("event_type", EventTypes.SYSTEM_ALERT)
        data = message.get("data", {"message": "Test event"})
        subscription = message.get("subscription")
        
        await broadcast_event(event_type, data, subscription)
        
        await manager.send_personal_message(websocket, {
            "type": "broadcast_sent",
            "event_type": event_type,
            "subscription": subscription
        })
        
    elif action == "get_connections":
        # Get connection statistics
        stats = manager.get_connection_stats()
        await manager.send_personal_message(websocket, {
            "type": "connection_stats",
            "data": stats
        })
        
    else:
        await manager.send_personal_message(websocket, {
            "type": "error",
            "message": f"Unknown admin action: {action}"
        })

# Utility functions for other parts of the application to trigger events
async def notify_machine_status_change(machine_id: str, status: str, utilization: Optional[float] = None):
    """Notify clients of machine status changes."""
    data = {
        "machine_id": machine_id,
        "status": status,
        "utilization": utilization
    }
    await broadcast_event(EventTypes.MACHINE_STATUS_UPDATE, data, "machines")

async def notify_maintenance_alert(ticket_id: int, machine_id: str, priority: str, description: str):
    """Notify clients of new maintenance alerts."""
    data = {
        "ticket_id": ticket_id,
        "machine_id": machine_id, 
        "priority": priority,
        "description": description
    }
    await broadcast_event(EventTypes.MAINTENANCE_ALERT, data, "maintenance")

async def notify_production_update(metrics: dict):
    """Notify clients of production metric updates."""
    await broadcast_event(EventTypes.PRODUCTION_METRIC_UPDATE, metrics, "production")

async def notify_dashboard_refresh():
    """Trigger dashboard refresh for all clients."""
    data = {"refresh_all": True}
    await broadcast_event(EventTypes.DASHBOARD_REFRESH, data, "dashboard")

async def notify_ticket_status_change(ticket_id: int, old_status: str, new_status: str, machine_id: str):
    """Notify clients of ticket status changes."""
    data = {
        "ticket_id": ticket_id,
        "old_status": old_status,
        "new_status": new_status,
        "machine_id": machine_id
    }
    await broadcast_event(EventTypes.TICKET_STATUS_CHANGE, data, "maintenance")
