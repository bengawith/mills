"""
Event dispatcher for WebSocket notifications.
Handles async WebSocket events from synchronous service methods.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class EventDispatcher:
    """Dispatches events to WebSocket clients in a thread-safe manner."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.loop = None
        
    def get_or_create_event_loop(self):
        """Get the current event loop or create a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def dispatch_maintenance_alert(self, ticket_id: int, machine_id: str, priority: str, description: str):
        """Dispatch maintenance alert event."""
        try:
            # Import here to avoid circular imports
            from routers.websocket import notify_maintenance_alert
            
            # Schedule the coroutine to run in the event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, schedule the task
                task = loop.create_task(notify_maintenance_alert(ticket_id, machine_id, priority, description))
                logger.debug(f"Scheduled maintenance alert for ticket {ticket_id}")
            except RuntimeError:
                # Not in an async context, run in executor
                asyncio.run(notify_maintenance_alert(ticket_id, machine_id, priority, description))
                logger.debug(f"Dispatched maintenance alert for ticket {ticket_id}")
                
        except Exception as e:
            logger.error(f"Failed to dispatch maintenance alert: {e}")
    
    def dispatch_ticket_status_change(self, ticket_id: int, old_status: str, new_status: str, machine_id: str):
        """Dispatch ticket status change event."""
        try:
            from routers.websocket import notify_ticket_status_change
            
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(notify_ticket_status_change(ticket_id, old_status, new_status, machine_id))
                logger.debug(f"Scheduled status change for ticket {ticket_id}: {old_status} -> {new_status}")
            except RuntimeError:
                asyncio.run(notify_ticket_status_change(ticket_id, old_status, new_status, machine_id))
                logger.debug(f"Dispatched status change for ticket {ticket_id}: {old_status} -> {new_status}")
                
        except Exception as e:
            logger.error(f"Failed to dispatch ticket status change: {e}")
    
    def dispatch_machine_status_change(self, machine_id: str, status: str, utilization: Optional[float] = None):
        """Dispatch machine status change event."""
        try:
            from routers.websocket import notify_machine_status_change
            
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(notify_machine_status_change(machine_id, status, utilization))
                logger.debug(f"Scheduled machine status change for {machine_id}: {status}")
            except RuntimeError:
                asyncio.run(notify_machine_status_change(machine_id, status, utilization))
                logger.debug(f"Dispatched machine status change for {machine_id}: {status}")
                
        except Exception as e:
            logger.error(f"Failed to dispatch machine status change: {e}")

    def dispatch_ticket_created(self, ticket: dict):
        """Dispatch ticket created event."""
        try:
            from routers.websocket import notify_ticket_created
            
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(notify_ticket_created(ticket))
                logger.debug(f"Scheduled ticket created for ticket {ticket.get('id')}")
            except RuntimeError:
                asyncio.run(notify_ticket_created(ticket))
                logger.debug(f"Dispatched ticket created for ticket {ticket.get('id')}")
                
        except Exception as e:
            logger.error(f"Failed to dispatch ticket created event: {e}")
    
    def dispatch_dashboard_refresh(self):
        """Trigger dashboard refresh for all clients."""
        try:
            from routers.websocket import notify_dashboard_refresh
            
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(notify_dashboard_refresh())
                logger.debug("Scheduled dashboard refresh")
            except RuntimeError:
                asyncio.run(notify_dashboard_refresh())
                logger.debug("Dispatched dashboard refresh")
                
        except Exception as e:
            logger.error(f"Failed to dispatch dashboard refresh: {e}")

# Global event dispatcher instance
event_dispatcher = EventDispatcher()
