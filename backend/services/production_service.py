"""
Production data service layer.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime, timezone, timedelta
import logging

from services.base_service import BaseService
from database_models import CutEvent, HistoricalMachineData

logger = logging.getLogger(__name__)

class ProductionService(BaseService):
    """
    Service class for production data operations.
    Provides methods for summarizing production events, calculating cut frequency, and other analytics.
    Inherits from BaseService for common CRUD operations.
    """
    
    def __init__(self) -> None:
        """
        Initialize ProductionService with CutEvent as the model.
        """
        super().__init__(CutEvent)
    
    def get_production_summary(
        self,
        db: Session,
        machine_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get production summary for specified period.
        
        Args:
            db (Session): SQLAlchemy database session.
            machine_id (Optional[str]): Machine ID to filter.
            start_date (Optional[datetime]): Start of time range (UTC).
            end_date (Optional[datetime]): End of time range (UTC).
        
        Returns:
            Dict[str, Any]: Dictionary with total cuts, total events, and cut frequency.
        """
        try:
            query = db.query(CutEvent)
            
            if machine_id:
                query = query.filter(CutEvent.machine_id == machine_id)
            
            if start_date:
                query = query.filter(CutEvent.timestamp_utc >= start_date)
            
            if end_date:
                query = query.filter(CutEvent.timestamp_utc <= end_date)
            
            events = query.all()
            
            if not events:
                return {
                    "total_cuts": 0,
                    "total_events": 0,
                    "cut_frequency": 0
                }
            
            # Calculate totals
            total_cuts = 0
            for event in events:
                if hasattr(event, 'cut_count') and event.cut_count is not None:
                    total_cuts += event.cut_count
            
            total_events = len(events)
            
            # Calculate frequency using SQL to avoid column type issues
            if len(events) > 1:
                # Use SQL ordering to get first and last timestamps
                first_event = query.order_by(CutEvent.timestamp_utc.asc()).first()
                last_event = query.order_by(CutEvent.timestamp_utc.desc()).first()
                
                if first_event and last_event:
                    time_span = (last_event.timestamp_utc - first_event.timestamp_utc).total_seconds()
                    cut_frequency = total_cuts / (time_span / 3600) if time_span > 0 else 0
                else:
                    cut_frequency = 0
            else:
                cut_frequency = 0
            
            return {
                "total_cuts": total_cuts,
                "total_events": total_events,
                "cut_frequency": cut_frequency
            }
        except SQLAlchemyError as e:
            logger.error(f"Error calculating production summary: {str(e)}")
            raise
    
    def get_daily_production(
        self,
        db: Session,
        date: datetime,
        machine_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get production data for a specific day.
        
        Args:
            db (Session): SQLAlchemy database session.
            date (datetime): Date for which to get production data.
            machine_id (Optional[str]): Machine ID to filter.
        
        Returns:
            Dict[str, Any]: Dictionary with daily production summary.
        """
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            return self.get_production_summary(
                db, machine_id, start_of_day, end_of_day
            )
        except Exception as e:
            logger.error(f"Error getting daily production: {str(e)}")
            raise
    
    def get_machine_utilization(
        self,
        db: Session,
        machine_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate machine utilization based on cut events frequency.
        
        Args:
            db (Session): SQLAlchemy database session.
            machine_id (str): Machine ID to calculate utilization for.
            start_date (Optional[datetime]): Start of time range (UTC).
            end_date (Optional[datetime]): End of time range (UTC).
        
        Returns:
            Dict[str, Any]: Dictionary with utilization metrics.
        """
        try:
            if not start_date:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
            if not end_date:
                end_date = datetime.now(timezone.utc)
            
            # Get cut events in the period
            query = db.query(CutEvent)\
                     .filter(CutEvent.machine_id == machine_id)\
                     .filter(CutEvent.timestamp_utc >= start_date)\
                     .filter(CutEvent.timestamp_utc <= end_date)
            
            events = query.all()
            
            total_period_hours = (end_date - start_date).total_seconds() / 3600
            
            # Calculate total cuts
            total_cuts = 0
            for event in events:
                if hasattr(event, 'cut_count') and event.cut_count is not None:
                    total_cuts += event.cut_count
            
            # Estimate utilization based on cut frequency
            # Assume normal operation is about 60 cuts per hour
            expected_cuts = total_period_hours * 60
            if expected_cuts > 0:
                utilization = float(total_cuts / expected_cuts * 100)
                utilization = min(utilization, 100.0)  # Cap at 100%
            else:
                utilization = 0.0
            
            return {
                "utilization_percentage": float(utilization),
                "total_cuts": total_cuts,
                "total_period_hours": total_period_hours
            }
        except SQLAlchemyError as e:
            logger.error(f"Error calculating machine utilization: {str(e)}")
            raise
    
    def get_top_performing_machines(self, db: Session, limit: int = 5,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get top performing machines by cut count."""
        try:
            if not start_date:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
            if not end_date:
                end_date = datetime.now(timezone.utc)
            
            # Query for machine performance using aggregation
            result = db.query(
                CutEvent.machine_id,
                func.count(CutEvent.id).label('event_count'),
                func.sum(CutEvent.cut_count).label('total_cuts')
            ).filter(
                CutEvent.timestamp_utc >= start_date,
                CutEvent.timestamp_utc <= end_date
            ).group_by(
                CutEvent.machine_id
            ).order_by(
                desc('total_cuts')
            ).limit(limit).all()
            
            machines = []
            for row in result:
                machines.append({
                    "machine_id": row.machine_id,
                    "event_count": row.event_count,
                    "total_cuts": row.total_cuts if row.total_cuts else 0
                })
            
            return machines
        except SQLAlchemyError as e:
            logger.error(f"Error getting top performing machines: {str(e)}")
            raise
    
    def get_recent_cuts(self, db: Session, machine_id: Optional[str] = None,
                       limit: int = 50) -> List[CutEvent]:
        """Get recent cut events."""
        try:
            query = db.query(CutEvent)
            
            if machine_id:
                query = query.filter(CutEvent.machine_id == machine_id)
            
            return query.order_by(desc(CutEvent.timestamp_utc)).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent cuts: {str(e)}")
            raise
    
    def get_production_trends(self, db: Session, machine_id: Optional[str] = None,
                            days: int = 30) -> List[Dict[str, Any]]:
        """Get daily production trends over specified period."""
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            trends = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                daily_data = self.get_daily_production(db, date, machine_id)
                daily_data['date'] = date.date().isoformat()
                trends.append(daily_data)
            
            return trends
        except Exception as e:
            logger.error(f"Error getting production trends: {str(e)}")
            raise

class MachineService(BaseService):
    """Service class for machine operations."""
    
    def __init__(self):
        super().__init__(HistoricalMachineData)
    
    def get_machine_status(self, db: Session, machine_id: str) -> Dict[str, Any]:
        """Get current status of a machine."""
        try:
            # Get machine info from historical data
            machine_info = db.query(HistoricalMachineData)\
                            .filter(HistoricalMachineData.machine_id == machine_id)\
                            .first()
            
            # Get latest cut event
            latest_cut = db.query(CutEvent)\
                          .filter(CutEvent.machine_id == machine_id)\
                          .order_by(desc(CutEvent.timestamp_utc))\
                          .first()
            
            status = {
                "machine_id": machine_id,
                "name": machine_info.name if machine_info else f"Machine {machine_id}",
                "last_activity": latest_cut.timestamp_utc if latest_cut else None,
                "is_active": False
            }
            
            # Determine if machine is currently active (cut within last 10 minutes)
            if latest_cut:
                time_since_last_cut = datetime.now(timezone.utc) - latest_cut.timestamp_utc
                status["is_active"] = time_since_last_cut < timedelta(minutes=10)
            
            return status
        except SQLAlchemyError as e:
            logger.error(f"Error getting machine status: {str(e)}")
            raise
    
    def get_all_machines_status(self, db: Session) -> List[Dict[str, Any]]:
        """Get status of all machines."""
        try:
            # Get unique machine IDs from cut events and historical data
            cut_machines = db.query(CutEvent.machine_id).distinct().all()
            historical_machines = db.query(HistoricalMachineData.machine_id).distinct().all()
            
            all_machine_ids = set()
            for m in cut_machines:
                all_machine_ids.add(m.machine_id)
            for m in historical_machines:
                all_machine_ids.add(m.machine_id)
            
            return [self.get_machine_status(db, machine_id) for machine_id in all_machine_ids]
        except SQLAlchemyError as e:
            logger.error(f"Error getting all machines status: {str(e)}")
            raise
