"""
Optimized dashboard service using service layer.
This service provides optimized endpoints that avoid heavy pandas processing.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from datetime import datetime, timezone, timedelta
import logging

from database import get_db
from security import get_current_active_user
from services.production_service import ProductionService, MachineService
from services.maintenance_service import MaintenanceService
from const.config import config
import database_models

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Optimized Dashboard"],
    dependencies=[Depends(get_current_active_user)]
)

# Initialize services
production_service = ProductionService()
machine_service = MachineService()
maintenance_service = MaintenanceService()

@router.get("/analytical-data-optimized")
def get_analytical_data_optimized(
    start_time: datetime,
    end_time: datetime,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Optimized version of analytical data endpoint using direct SQL queries
    instead of heavy pandas processing.
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
        
        # Enrich with production and maintenance data using SQL joins
        enriched_data = []
        
        for event in historical_data:
            event_dict = {
                "id": event.id,
                "machine_id": event.machine_id,
                "name": event.name,
                "downtime_reason_name": event.downtime_reason_name,
                "start_timestamp": event.start_timestamp,
                "end_timestamp": event.end_timestamp,
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
            
            # Find overlapping production run using SQL
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
            
            # Find linked maintenance ticket
            if event.id:  # fourjaw_downtime_id
                maintenance_ticket = db.query(database_models.MaintenanceTicket).filter(
                    database_models.MaintenanceTicket.fourjaw_downtime_id == event.id
                ).first()
                
                if maintenance_ticket:
                    event_dict["maintenance_ticket_id"] = maintenance_ticket.id
                    event_dict["incident_category"] = maintenance_ticket.incident_category
            
            enriched_data.append(event_dict)
        
        logger.info(f"Optimized query returned {len(enriched_data)} enriched records")
        return enriched_data
        
    except Exception as e:
        logger.error(f"Error in optimized analytical data endpoint: {str(e)}")
        raise

@router.get("/machine-summary")
def get_machine_summary(
    machine_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get machine status summary using optimized service layer.
    """
    try:
        if machine_ids is None:
            machine_ids = config.MACHINE_IDS
        
        summaries = []
        for machine_id in machine_ids:
            status = machine_service.get_machine_status(db, machine_id)
            
            # Get today's production summary
            today_production = production_service.get_daily_production(
                db, datetime.now(timezone.utc), machine_id
            )
            
            # Get recent maintenance tickets
            recent_tickets = maintenance_service.get_tickets_by_machine(db, machine_id)
            open_tickets = [t for t in recent_tickets if t.status == "Open"]
            
            summary = {
                **status,
                "today_cuts": today_production.get("total_cuts", 0),
                "today_events": today_production.get("total_events", 0),
                "cut_frequency": today_production.get("cut_frequency", 0),
                "open_tickets": len(open_tickets),
                "total_tickets": len(recent_tickets)
            }
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error in machine summary endpoint: {str(e)}")
        raise

@router.get("/production-metrics")
def get_production_metrics(
    start_time: datetime,
    end_time: datetime,
    machine_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get aggregated production metrics using optimized queries.
    """
    try:
        if machine_ids is None:
            machine_ids = config.MACHINE_IDS
        
        metrics = {}
        
        for machine_id in machine_ids:
            # Get production summary
            summary = production_service.get_production_summary(
                db, machine_id, start_time, end_time
            )
            
            # Get utilization (simplified calculation)
            total_period_hours = (end_time - start_time).total_seconds() / 3600
            cut_frequency = summary.get("cut_frequency", 0)
            
            # Estimate utilization based on cut frequency
            # Assume normal operation is about 60 cuts per hour
            expected_cuts_per_hour = 60
            utilization = min((cut_frequency / expected_cuts_per_hour) * 100, 100) if cut_frequency > 0 else 0
            
            metrics[machine_id] = {
                **summary,
                "utilization_percentage": utilization,
                "period_hours": total_period_hours
            }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error in production metrics endpoint: {str(e)}")
        raise

@router.get("/maintenance-overview")
def get_maintenance_overview(
    machine_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get maintenance overview using service layer.
    """
    try:
        if machine_ids is None:
            machine_ids = config.MACHINE_IDS
        
        # Get overall statistics
        stats = maintenance_service.get_ticket_statistics(db)
        
        # Get machine-specific data
        machine_data = {}
        for machine_id in machine_ids:
            tickets = maintenance_service.get_tickets_by_machine(db, machine_id)
            open_tickets = [t for t in tickets if t.status == "Open"]
            high_priority = [t for t in open_tickets if t.priority == "High"]
            
            machine_data[machine_id] = {
                "total_tickets": len(tickets),
                "open_tickets": len(open_tickets),
                "high_priority_open": len(high_priority)
            }
        
        return {
            "overall_stats": stats,
            "machine_breakdown": machine_data
        }
        
    except Exception as e:
        logger.error(f"Error in maintenance overview endpoint: {str(e)}")
        raise

@router.get("/quick-stats")
def get_quick_stats(db: Session = Depends(get_db)):
    """
    Get quick dashboard statistics using efficient queries.
    """
    try:
        # Count queries are optimized by default
        total_machines = len(config.MACHINE_IDS)
        
        # Active machines (had cuts in last 10 minutes)
        recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        active_machines_count = db.query(func.count(func.distinct(
            database_models.CutEvent.machine_id
        ))).filter(
            database_models.CutEvent.timestamp_utc >= recent_time,
            database_models.CutEvent.machine_id.in_(config.MACHINE_IDS)
        ).scalar()
        
        # Today's total cuts
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_cuts = db.query(func.sum(database_models.CutEvent.cut_count)).filter(
            database_models.CutEvent.timestamp_utc >= today_start,
            database_models.CutEvent.machine_id.in_(config.MACHINE_IDS)
        ).scalar() or 0
        
        # Open maintenance tickets
        open_tickets = db.query(func.count(database_models.MaintenanceTicket.id)).filter(
            database_models.MaintenanceTicket.status == "Open",
            database_models.MaintenanceTicket.machine_id.in_(config.MACHINE_IDS)
        ).scalar()
        
        # High priority tickets
        high_priority_tickets = db.query(func.count(database_models.MaintenanceTicket.id)).filter(
            database_models.MaintenanceTicket.status == "Open",
            database_models.MaintenanceTicket.priority == "High",
            database_models.MaintenanceTicket.machine_id.in_(config.MACHINE_IDS)
        ).scalar()
        
        return {
            "total_machines": total_machines,
            "active_machines": active_machines_count or 0,
            "today_total_cuts": int(today_cuts),
            "open_tickets": open_tickets or 0,
            "high_priority_tickets": high_priority_tickets or 0,
            "machine_utilization": round((active_machines_count or 0) / total_machines * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error in quick stats endpoint: {str(e)}")
        raise
