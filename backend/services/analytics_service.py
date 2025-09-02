"""
High-performance analytics service using direct SQL optimization.
This service replaces pandas-heavy operations with optimized SQL queries.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, text
from datetime import datetime, timezone, timedelta
import logging

from services.base_service import BaseService
from database_models import (
    HistoricalMachineData, CutEvent, MaintenanceTicket, 
    ProductionRun, Product, AnalyticalDataSummary, 
    MachineStatusCache, DowntimeSummary
)
from const.config import config

logger = logging.getLogger(__name__)

class AnalyticsService(BaseService):
    """
    Optimized analytics service using SQL-first approach.
    Provides high-performance endpoints for OEE, utilization, and downtime analysis.
    Inherits from BaseService for common DB operations.
    """
    
    def __init__(self):
        super().__init__(HistoricalMachineData)
    
    def get_optimized_oee(
        self,
        db: Session,
        machine_ids: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        shift: Optional[str] = None,
        day_of_week: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate OEE using optimized SQL aggregations.
        
        Args:
            db (Session): SQLAlchemy database session.
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            shift (Optional[str]): Shift name to filter.
            day_of_week (Optional[str]): Day of week to filter.
        
        Returns:
            Dict[str, float]: Dictionary with OEE, availability, performance, and quality metrics.
        """
        try:
            if machine_ids is None:
                machine_ids = config.MACHINE_IDS
            
            # Build base query with filters
            query = db.query(
                func.sum(HistoricalMachineData.duration_seconds).label('total_time'),
                func.sum(
                    case(
                        (HistoricalMachineData.classification == 'UPTIME', 
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('uptime'),
                func.sum(
                    case(
                        ((HistoricalMachineData.classification == 'UPTIME') & 
                         (HistoricalMachineData.productivity == 'productive'),
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('productive_time')
            ).filter(
                HistoricalMachineData.machine_id.in_(machine_ids)
            )
            
            # Apply time filters
            if start_time:
                query = query.filter(HistoricalMachineData.start_timestamp >= start_time)
            if end_time:
                query = query.filter(HistoricalMachineData.end_timestamp <= end_time)
            if shift:
                query = query.filter(HistoricalMachineData.shift == shift)
            if day_of_week:
                query = query.filter(HistoricalMachineData.day_of_week == day_of_week)
            
            result = query.one()
            
            total_time = float(result.total_time or 0)
            uptime = float(result.uptime or 0)
            productive_time = float(result.productive_time or 0)
            
            if total_time == 0:
                return {"oee": 0.0, "availability": 0.0, "performance": 100.0, "quality": 100.0}
            
            # Calculate metrics
            availability = (uptime / total_time) * 100 if total_time > 0 else 0
            performance = 100.0  # Placeholder - would need part count data
            quality = 100.0     # Placeholder - would need quality data
            oee = (availability * performance * quality) / 10000  # Convert from percentage
            
            return {
                "oee": round(oee, 2),
                "availability": round(availability, 2),
                "performance": round(performance, 2),
                "quality": round(quality, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimized OEE: {str(e)}")
            raise
    
    def get_optimized_utilization(
        self,
        db: Session,
        machine_ids: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        shift: Optional[str] = None,
        day_of_week: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate utilization using optimized SQL aggregations.
        
        Args:
            db (Session): SQLAlchemy database session.
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            shift (Optional[str]): Shift name to filter.
            day_of_week (Optional[str]): Day of week to filter.
        
        Returns:
            Dict[str, float]: Dictionary with utilization metrics.
        """
        try:
            if machine_ids is None:
                machine_ids = config.MACHINE_IDS
            
            # Single SQL query to get all utilization components
            query = db.query(
                func.sum(HistoricalMachineData.duration_seconds).label('total_time'),
                func.sum(
                    case(
                        ((HistoricalMachineData.classification == 'UPTIME') & 
                         (HistoricalMachineData.productivity == 'productive'),
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('productive_uptime'),
                func.sum(
                    case(
                        ((HistoricalMachineData.classification == 'DOWNTIME') & 
                         (HistoricalMachineData.productivity == 'unproductive'),
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('unproductive_downtime'),
                func.sum(
                    case(
                        ((HistoricalMachineData.classification == 'DOWNTIME') & 
                         (HistoricalMachineData.productivity == 'productive'),
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('productive_downtime')
            ).filter(
                HistoricalMachineData.machine_id.in_(machine_ids)
            )
            
            # Apply filters
            if start_time:
                query = query.filter(HistoricalMachineData.start_timestamp >= start_time)
            if end_time:
                query = query.filter(HistoricalMachineData.end_timestamp <= end_time)
            if shift:
                query = query.filter(HistoricalMachineData.shift == shift)
            if day_of_week:
                query = query.filter(HistoricalMachineData.day_of_week == day_of_week)
            
            result = query.one()
            
            total_time = float(result.total_time or 0)
            productive_uptime = float(result.productive_uptime or 0)
            unproductive_downtime = float(result.unproductive_downtime or 0)
            productive_downtime = float(result.productive_downtime or 0)
            
            # Calculate utilization percentage
            utilization = 0.0
            if total_time > 0:
                utilization = (productive_uptime / total_time) * 100
            
            return {
                "total_time_seconds": round(total_time, 2),
                "productive_uptime_seconds": round(productive_uptime, 2),
                "unproductive_downtime_seconds": round(unproductive_downtime, 2),
                "productive_downtime_seconds": round(productive_downtime, 2),
                "utilization_percentage": round(utilization, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimized utilization: {str(e)}")
            raise
    
    def get_optimized_downtime_analysis(
        self,
        db: Session,
        machine_ids: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        shift: Optional[str] = None,
        day_of_week: Optional[str] = None,
        excessive_threshold: int = 3600
    ) -> Dict[str, Any]:
        """
        Analyze downtime using optimized SQL queries.
        
        Args:
            db (Session): SQLAlchemy database session.
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            shift (Optional[str]): Shift name to filter.
            day_of_week (Optional[str]): Day of week to filter.
            excessive_threshold (int): Threshold for excessive downtime (seconds).
        
        Returns:
            Dict[str, Any]: Dictionary with downtime analysis results.
        """
        try:
            if machine_ids is None:
                machine_ids = config.MACHINE_IDS
            
            # Base downtime query
            base_query = db.query(HistoricalMachineData).filter(
                HistoricalMachineData.machine_id.in_(machine_ids),
                HistoricalMachineData.classification == 'DOWNTIME'
            )
            
            # Apply filters
            if start_time:
                base_query = base_query.filter(HistoricalMachineData.start_timestamp >= start_time)
            if end_time:
                base_query = base_query.filter(HistoricalMachineData.end_timestamp <= end_time)
            if shift:
                base_query = base_query.filter(HistoricalMachineData.shift == shift)
            if day_of_week:
                base_query = base_query.filter(HistoricalMachineData.day_of_week == day_of_week)
            
            # Get excessive downtimes in one query
            excessive_downtimes = base_query.filter(
                HistoricalMachineData.duration_seconds > excessive_threshold
            ).all()
            
            excessive_list = []
            for event in excessive_downtimes:
                excessive_list.append({
                    "name": getattr(event, 'name', ''),
                    "machine_id": event.machine_id,
                    "downtime_reason_name": event.downtime_reason_name or '',
                    "duration_seconds": event.duration_seconds,
                    "start_timestamp": event.start_timestamp,
                    "end_timestamp": event.end_timestamp
                })
            
            # Get recurring downtime reasons using SQL aggregation
            recurring_query = db.query(
                HistoricalMachineData.downtime_reason_name,
                func.sum(HistoricalMachineData.duration_seconds).label('total_duration')
            ).filter(
                HistoricalMachineData.machine_id.in_(machine_ids),
                HistoricalMachineData.classification == 'DOWNTIME',
                HistoricalMachineData.downtime_reason_name.isnot(None)
            )
            
            # Apply same filters
            if start_time:
                recurring_query = recurring_query.filter(HistoricalMachineData.start_timestamp >= start_time)
            if end_time:
                recurring_query = recurring_query.filter(HistoricalMachineData.end_timestamp <= end_time)
            if shift:
                recurring_query = recurring_query.filter(HistoricalMachineData.shift == shift)
            if day_of_week:
                recurring_query = recurring_query.filter(HistoricalMachineData.day_of_week == day_of_week)
            
            recurring_results = recurring_query.group_by(
                HistoricalMachineData.downtime_reason_name
            ).order_by(
                func.sum(HistoricalMachineData.duration_seconds).desc()
            ).all()
            
            recurring_dict = {
                result.downtime_reason_name: float(result.total_duration)
                for result in recurring_results
            }
            
            return {
                "excessive_downtimes": excessive_list,
                "recurring_downtime_reasons": recurring_dict
            }
            
        except Exception as e:
            logger.error(f"Error in optimized downtime analysis: {str(e)}")
            raise
    
    def get_machine_performance_summary(self, db: Session, machine_ids: Optional[List[str]] = None,
                                       hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Get performance summary for each machine using optimized queries.
        """
        try:
            if machine_ids is None:
                machine_ids = config.MACHINE_IDS
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            # Get machine performance data in one query
            performance_query = db.query(
                HistoricalMachineData.machine_id,
                func.sum(HistoricalMachineData.duration_seconds).label('total_time'),
                func.sum(
                    case(
                        (HistoricalMachineData.classification == 'UPTIME',
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('uptime'),
                func.count(
                    case(
                        (HistoricalMachineData.classification == 'DOWNTIME', 1),
                        else_=None
                    )
                ).label('downtime_events')
            ).filter(
                HistoricalMachineData.machine_id.in_(machine_ids),
                HistoricalMachineData.start_timestamp >= cutoff_time
            ).group_by(HistoricalMachineData.machine_id).all()
            
            # Get cut event data for the same period
            cut_data_query = db.query(
                CutEvent.machine_id,
                func.sum(CutEvent.cut_count).label('total_cuts'),
                func.count(CutEvent.id).label('cut_events')
            ).filter(
                CutEvent.machine_id.in_(machine_ids),
                CutEvent.timestamp_utc >= cutoff_time
            ).group_by(CutEvent.machine_id).all()
            
            # Convert to dictionaries for easy lookup
            cut_data_dict = {
                row.machine_id: {
                    'total_cuts': int(row.total_cuts or 0),
                    'cut_events': int(row.cut_events or 0)
                }
                for row in cut_data_query
            }
            
            # Get current machine status from cache if available
            status_cache = db.query(MachineStatusCache).filter(
                MachineStatusCache.machine_id.in_(machine_ids)
            ).all()
            
            status_dict = {
                cache.machine_id: {
                    'current_status': cache.current_status,
                    'last_event_time': cache.last_event_time
                }
                for cache in status_cache
            }
            
            # Combine results
            results = []
            for row in performance_query:
                machine_id = row.machine_id
                total_time = float(row.total_time or 0)
                uptime = float(row.uptime or 0)
                
                utilization = (uptime / total_time * 100) if total_time > 0 else 0
                
                cut_info = cut_data_dict.get(machine_id, {'total_cuts': 0, 'cut_events': 0})
                status_info = status_dict.get(machine_id, {'current_status': 'Unknown', 'last_event_time': None})
                
                results.append({
                    'machine_id': machine_id,
                    'machine_name': config.MACHINE_ID_MAP.get(machine_id, machine_id),
                    'utilization_percentage': round(utilization, 2),
                    'total_cuts': cut_info['total_cuts'],
                    'total_time_hours': round(total_time / 3600, 2),
                    'uptime_hours': round(uptime / 3600, 2),
                    'downtime_events': int(row.downtime_events or 0),
                    'current_status': status_info['current_status'],
                    'last_event_time': status_info['last_event_time']
                })
            
            return sorted(results, key=lambda x: x['utilization_percentage'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting machine performance summary: {str(e)}")
            raise
    
    def get_real_time_metrics(self, db: Session) -> Dict[str, Any]:
        """
        Get real-time metrics using cached data and optimized queries.
        """
        try:
            # Use summary tables for faster queries
            recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)
            
            # Active machines based on recent cuts
            active_machines = db.query(
                func.count(func.distinct(CutEvent.machine_id))
            ).filter(
                CutEvent.timestamp_utc >= recent_time,
                CutEvent.machine_id.in_(config.MACHINE_IDS)
            ).scalar() or 0
            
            # Today's production from summary or direct calculation
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            
            today_cuts = db.query(
                func.sum(CutEvent.cut_count)
            ).filter(
                CutEvent.timestamp_utc >= today_start,
                CutEvent.machine_id.in_(config.MACHINE_IDS)
            ).scalar() or 0
            
            # Open tickets
            open_tickets = db.query(
                func.count(MaintenanceTicket.id)
            ).filter(
                MaintenanceTicket.status == "Open",
                MaintenanceTicket.machine_id.in_(config.MACHINE_IDS)
            ).scalar() or 0
            
            # High priority tickets
            high_priority = db.query(
                func.count(MaintenanceTicket.id)
            ).filter(
                MaintenanceTicket.status == "Open",
                MaintenanceTicket.priority == "High",
                MaintenanceTicket.machine_id.in_(config.MACHINE_IDS)
            ).scalar() or 0
            
            # Overall utilization from cache or calculation
            overall_utilization = (active_machines / len(config.MACHINE_IDS) * 100) if config.MACHINE_IDS else 0
            
            return {
                "total_machines": len(config.MACHINE_IDS),
                "active_machines": int(active_machines),
                "today_total_cuts": int(today_cuts),
                "open_tickets": int(open_tickets),
                "high_priority_tickets": int(high_priority),
                "overall_utilization": round(overall_utilization, 1),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            raise
    
    def get_trend_data(self, db: Session, machine_ids: Optional[List[str]] = None,
                      days_back: int = 30, interval: str = 'daily') -> List[Dict[str, Any]]:
        """
        Get trend data for charts using optimized time-based aggregations.
        """
        try:
            if machine_ids is None:
                machine_ids = config.MACHINE_IDS
            
            start_time = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            # Determine grouping based on interval
            if interval == 'hourly':
                time_group = [
                    extract('year', HistoricalMachineData.start_timestamp),
                    extract('month', HistoricalMachineData.start_timestamp),
                    extract('day', HistoricalMachineData.start_timestamp),
                    extract('hour', HistoricalMachineData.start_timestamp)
                ]
                time_format = 'hour'
            else:  # daily
                time_group = [
                    extract('year', HistoricalMachineData.start_timestamp),
                    extract('month', HistoricalMachineData.start_timestamp),
                    extract('day', HistoricalMachineData.start_timestamp)
                ]
                time_format = 'day'
            
            # Query for trend data
            trend_query = db.query(
                extract('year', HistoricalMachineData.start_timestamp).label('year'),
                extract('month', HistoricalMachineData.start_timestamp).label('month'),
                extract('day', HistoricalMachineData.start_timestamp).label('day'),
                extract('hour', HistoricalMachineData.start_timestamp).label('hour') if interval == 'hourly' else None,
                func.sum(HistoricalMachineData.duration_seconds).label('total_time'),
                func.sum(
                    case(
                        (HistoricalMachineData.classification == 'UPTIME',
                         HistoricalMachineData.duration_seconds),
                        else_=0
                    )
                ).label('uptime'),
                func.count(HistoricalMachineData.id).label('total_events')
            ).filter(
                HistoricalMachineData.machine_id.in_(machine_ids),
                HistoricalMachineData.start_timestamp >= start_time
            ).group_by(*time_group).order_by(*time_group).all()
            
            # Format results
            trends = []
            for row in trend_query:
                if interval == 'hourly':
                    timestamp = datetime(
                        year=int(row.year), month=int(row.month), 
                        day=int(row.day), hour=int(row.hour or 0)
                    )
                else:
                    timestamp = datetime(
                        year=int(row.year), month=int(row.month), day=int(row.day)
                    )
                
                total_time = float(row.total_time or 0)
                uptime = float(row.uptime or 0)
                utilization = (uptime / total_time * 100) if total_time > 0 else 0
                
                trends.append({
                    'timestamp': timestamp.isoformat(),
                    'utilization_percentage': round(utilization, 2),
                    'total_events': int(row.total_events or 0),
                    'uptime_hours': round(uptime / 3600, 2),
                    'total_time_hours': round(total_time / 3600, 2)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trend data: {str(e)}")
            raise
