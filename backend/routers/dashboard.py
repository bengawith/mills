from typing import List, Optional
from fastapi import APIRouter, Depends, Query
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

import schemas
import database_models
from database import get_db
from security import get_current_active_user
from const.config import config
from services.production_service import ProductionService
from services.maintenance_service import MaintenanceService

# Initialize services
production_service = ProductionService()
maintenance_service = MaintenanceService()


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard Analytics"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/analytical-data")
def get_analytical_data(
    start_time: dt.datetime,
    end_time: dt.datetime,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Optimized version that maintains frontend compatibility while using 
    service layer and avoiding heavy pandas processing.
    """
    try:
        if machine_ids is None:
            machine_ids = config.MACHINE_IDS
        
        # Build optimized query for historical machine data
        query = db.query(database_models.HistoricalMachineData).filter(
            database_models.HistoricalMachineData.machine_id.in_(machine_ids),
            database_models.HistoricalMachineData.start_timestamp >= start_time,
            database_models.HistoricalMachineData.end_timestamp <= end_time
        )
        
        # Apply filters
        if shift and shift != "All":
            query = query.filter(database_models.HistoricalMachineData.shift == shift)
        
        if day_of_week and day_of_week != "All":
            query = query.filter(database_models.HistoricalMachineData.day_of_week == day_of_week)
        
        # Get data efficiently
        historical_data = query.all()
        
        if not historical_data:
            return []
        
        # Enrich with production and maintenance data using optimized SQL queries
        enriched_data = []
        
        for event in historical_data:
            event_dict = {
                "id": event.id,
                "machine_id": event.machine_id,
                "name": event.name,
                "downtime_reason_name": event.downtime_reason_name,
                "start_timestamp": event.start_timestamp.isoformat() if event.start_timestamp is not None else None,
                "end_timestamp": event.end_timestamp.isoformat() if event.end_timestamp is not None else None,
                "duration_seconds": event.duration_seconds,
                "productivity": event.productivity,
                "classification": event.classification,
                "shift": event.shift,
                "day_of_week": event.day_of_week,
                "utilisation_category": event.utilisation_category,
                "product_name": None,
                "maintenance_ticket_id": None,
                "incident_category": None
            }
            
            # Find overlapping production run using optimized SQL
            production_run = db.query(database_models.ProductionRun).join(
                database_models.Product
            ).filter(
                database_models.ProductionRun.machine_id == event.machine_id,
                database_models.ProductionRun.start_time <= event.start_timestamp,
                or_(
                    database_models.ProductionRun.end_time >= event.end_timestamp,
                    database_models.ProductionRun.end_time.is_(None)
                )
            ).first()
            
            if production_run and production_run.product:
                event_dict["product_name"] = production_run.product.product_name
            
            # Find linked maintenance ticket using optimized query
            if event.id is not None:  # This is the fourjaw_downtime_id
                maintenance_ticket = db.query(database_models.MaintenanceTicket).filter(
                    database_models.MaintenanceTicket.fourjaw_downtime_id == event.id
                ).first()
                
                if maintenance_ticket:
                    event_dict["maintenance_ticket_id"] = maintenance_ticket.id
                    event_dict["incident_category"] = maintenance_ticket.incident_category
            
            enriched_data.append(event_dict)
        
        return enriched_data
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in analytical data endpoint: {str(e)}")
        # Return empty list to maintain frontend compatibility
        return []
