"""
Maintenance management service layer.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging

from services.base_service import BaseService
from database_models import MaintenanceTicket, TicketWorkNote, TicketImage, RepairComponent, TicketComponentUsed
import schemas

logger = logging.getLogger(__name__)

class MaintenanceService(BaseService):
    """Service class for maintenance ticket operations."""
    
    def __init__(self):
        super().__init__(MaintenanceTicket)
    
    def create_ticket(self, db: Session, ticket_data: schemas.MaintenanceTicketCreate) -> MaintenanceTicket:
        """Create a new maintenance ticket."""
        try:
            ticket_dict = {
                "incident_category": ticket_data.incident_category,
                "description": ticket_data.description,
                "priority": ticket_data.priority,
                "machine_id": ticket_data.machine_id,
                "logged_time": datetime.now(timezone.utc),
                "status": "Open"
            }
            
            return self.create(db, ticket_dict)
        except SQLAlchemyError as e:
            logger.error(f"Error creating maintenance ticket: {str(e)}")
            raise
    
    def get_tickets_by_status(self, db: Session, status: str) -> List[MaintenanceTicket]:
        """Get tickets by status."""
        try:
            return db.query(MaintenanceTicket).filter(MaintenanceTicket.status == status).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching tickets by status {status}: {str(e)}")
            raise
    
    def get_tickets_by_machine(self, db: Session, machine_id: str) -> List[MaintenanceTicket]:
        """Get tickets for a specific machine."""
        try:
            return db.query(MaintenanceTicket)\
                     .filter(MaintenanceTicket.machine_id == machine_id)\
                     .order_by(MaintenanceTicket.logged_time.desc())\
                     .all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching tickets for machine {machine_id}: {str(e)}")
            raise
    
    def update_ticket_status(self, db: Session, ticket_id: int, status: str) -> Optional[MaintenanceTicket]:
        """Update ticket status."""
        try:
            update_data = {"status": status}
            if status.lower() in ["resolved", "closed"]:
                update_data["resolved_time"] = datetime.now(timezone.utc)
            
            return self.update(db, ticket_id, update_data)
        except SQLAlchemyError as e:
            logger.error(f"Error updating ticket {ticket_id} status: {str(e)}")
            raise
    
    def add_work_note(self, db: Session, ticket_id: int, note: str, author: str) -> TicketWorkNote:
        """Add a work note to a ticket."""
        try:
            work_note = TicketWorkNote(
                ticket_id=ticket_id,
                note=note,
                author=author,
                created_at=datetime.now(timezone.utc)
            )
            db.add(work_note)
            db.commit()
            db.refresh(work_note)
            logger.info(f"Added work note to ticket {ticket_id}")
            return work_note
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error adding work note to ticket {ticket_id}: {str(e)}")
            raise
    
    def get_open_tickets(self, db: Session) -> List[MaintenanceTicket]:
        """Get all open tickets."""
        return self.get_tickets_by_status(db, "Open")
    
    def get_ticket_statistics(self, db: Session) -> Dict[str, Any]:
        """Get maintenance ticket statistics."""
        try:
            total_tickets = db.query(MaintenanceTicket).count()
            open_tickets = db.query(MaintenanceTicket)\
                            .filter(MaintenanceTicket.status == "Open")\
                            .count()
            resolved_tickets = db.query(MaintenanceTicket)\
                             .filter(MaintenanceTicket.status.in_(["Resolved", "Closed"]))\
                             .count()
            
            # Get priority breakdown
            high_priority = db.query(MaintenanceTicket)\
                             .filter(MaintenanceTicket.priority == "High")\
                             .filter(MaintenanceTicket.status == "Open")\
                             .count()
            
            return {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "resolved_tickets": resolved_tickets,
                "high_priority_open": high_priority
            }
        except SQLAlchemyError as e:
            logger.error(f"Error calculating ticket statistics: {str(e)}")
            raise

class InventoryService(BaseService):
    """Service class for inventory and repair components."""
    
    def __init__(self):
        super().__init__(RepairComponent)
    
    def create_component(self, db: Session, component_data: schemas.RepairComponentCreate) -> RepairComponent:
        """Create a new repair component."""
        try:
            component_dict = {
                "component_name": component_data.component_name,
                "stock_code": component_data.stock_code,
                "current_stock": component_data.current_stock or 0
            }
            return self.create(db, component_dict)
        except SQLAlchemyError as e:
            logger.error(f"Error creating repair component: {str(e)}")
            raise
    
    def update_stock(self, db: Session, component_id: int, new_stock: int) -> Optional[RepairComponent]:
        """Update component stock level."""
        try:
            return self.update(db, component_id, {"current_stock": new_stock})
        except SQLAlchemyError as e:
            logger.error(f"Error updating stock for component {component_id}: {str(e)}")
            raise
    
    def get_low_stock_components(self, db: Session, threshold: int = 5) -> List[RepairComponent]:
        """Get components with low stock levels."""
        try:
            return db.query(RepairComponent)\
                     .filter(RepairComponent.current_stock <= threshold)\
                     .all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching low stock components: {str(e)}")
            raise
    
    def use_component_in_ticket(
        self, 
        db: Session, 
        ticket_id: int, 
        component_id: int, 
        quantity: int
    ) -> TicketComponentUsed:
        """Record component usage in a maintenance ticket and update stock."""
        try:
            # Check if component has sufficient stock
            component = self.get_by_id(db, component_id)
            if not component:
                raise ValueError(f"Component {component_id} not found")
            
            if component.current_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {component.current_stock}, Requested: {quantity}")
            
            # Create usage record
            usage = TicketComponentUsed(
                ticket_id=ticket_id,
                component_id=component_id,
                quantity_used=quantity
            )
            db.add(usage)
            
            # Update stock
            component.current_stock -= quantity
            
            db.commit()
            db.refresh(usage)
            
            logger.info(f"Used {quantity} units of component {component_id} in ticket {ticket_id}")
            return usage
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error using component in ticket: {str(e)}")
            raise
        except ValueError:
            raise
