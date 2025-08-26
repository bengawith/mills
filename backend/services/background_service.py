"""
Background data processing service using APScheduler.

This service handles background tasks for:
1. Pre-computing analytical data summaries
2. Updating machine status cache
3. Processing downtime analysis
4. Optimizing dashboard performance
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_, or_
import json

from database import SessionLocal
from database_models import (
    HistoricalMachineData, CutEvent, MaintenanceTicket, ProductionRun, Product,
    AnalyticalDataSummary, MachineStatusCache, DowntimeSummary
)
from const.config import config

logger = logging.getLogger(__name__)

class BackgroundDataProcessor:
    """Handles background data processing and summarization."""
    
    def __init__(self):
        self.config = config
    
    def process_daily_summaries(self, target_date: Optional[date] = None) -> bool:
        """Process daily analytical summaries for all machines."""
        if target_date is None:
            target_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()
        
        logger.info(f"Processing daily summaries for {target_date}")
        
        try:
            db = SessionLocal()
            try:
                success_count = 0
                for machine_id in self.config.MACHINE_IDS:
                    for shift in ['Day', 'Night', None]:  # None for all-day summary
                        if self._process_machine_daily_summary(db, machine_id, target_date, shift):
                            success_count += 1
                
                db.commit()
                logger.info(f"Successfully processed {success_count} daily summaries")
                return True
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing daily summaries: {str(e)}")
            return False
    
    def _process_machine_daily_summary(
        self, 
        db: Session, 
        machine_id: str, 
        target_date: date, 
        shift: Optional[str]
    ) -> bool:
        """Process daily summary for a specific machine and shift."""
        try:
            # Calculate date range
            start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=1)
            
            # Adjust for shift if specified
            if shift == 'Day':
                start_time = start_time.replace(hour=6)  # 6 AM start
                end_time = start_time.replace(hour=18)   # 6 PM end
            elif shift == 'Night':
                start_time = start_time.replace(hour=18)  # 6 PM start
                end_time = start_time + timedelta(hours=12)  # 6 AM next day
            
            # Get or create summary record
            summary = db.query(AnalyticalDataSummary).filter(
                AnalyticalDataSummary.machine_id == machine_id,
                AnalyticalDataSummary.date == target_date,
                AnalyticalDataSummary.shift == shift
            ).first()
            
            if not summary:
                summary = AnalyticalDataSummary(
                    machine_id=machine_id,
                    date=target_date,
                    shift=shift,
                    day_of_week=target_date.strftime('%A')
                )
                db.add(summary)
            
            # Process historical machine data
            historical_data = db.query(HistoricalMachineData).filter(
                HistoricalMachineData.machine_id == machine_id,
                HistoricalMachineData.start_timestamp >= start_time,
                HistoricalMachineData.end_timestamp <= end_time
            ).all()
            
            # Calculate metrics from historical data
            summary.total_events = len(historical_data)
            summary.productive_time_seconds = sum(
                event.duration_seconds for event in historical_data 
                if event.classification == 'Productive'
            )
            summary.downtime_seconds = sum(
                event.duration_seconds for event in historical_data 
                if event.classification in ['Downtime', 'Setup']
            )
            summary.setup_time_seconds = sum(
                event.duration_seconds for event in historical_data 
                if event.classification == 'Setup'
            )
            
            # Process cut events
            cut_events = db.query(CutEvent).filter(
                CutEvent.machine_id == machine_id,
                CutEvent.timestamp_utc >= start_time,
                CutEvent.timestamp_utc <= end_time
            ).all()
            
            summary.total_cuts = sum(event.cut_count or 0 for event in cut_events)
            
            # Calculate utilization and OEE
            total_time = (end_time - start_time).total_seconds()
            if total_time > 0:
                summary.utilization_percentage = (summary.productive_time_seconds / total_time) * 100
                summary.availability_percentage = ((total_time - summary.downtime_seconds) / total_time) * 100
                summary.performance_percentage = min(summary.utilization_percentage, 100.0)
                summary.quality_percentage = 95.0  # Placeholder - would need quality data
                summary.oee_percentage = (
                    summary.availability_percentage * 
                    summary.performance_percentage * 
                    summary.quality_percentage
                ) / 10000
            
            # Process maintenance data
            maintenance_tickets = db.query(MaintenanceTicket).filter(
                MaintenanceTicket.machine_id == machine_id,
                MaintenanceTicket.logged_time >= start_time,
                MaintenanceTicket.logged_time <= end_time
            ).all()
            
            summary.maintenance_tickets_count = len(maintenance_tickets)
            summary.critical_tickets_count = len([
                t for t in maintenance_tickets 
                if t.priority in ['High', 'Critical']
            ])
            
            # Process production runs
            production_runs = db.query(ProductionRun).join(Product).filter(
                ProductionRun.machine_id == machine_id,
                ProductionRun.start_time >= start_time,
                ProductionRun.start_time <= end_time
            ).all()
            
            summary.production_runs_count = len(production_runs)
            products = list(set([run.product.product_name for run in production_runs if run.product]))
            summary.products_produced = json.dumps(products) if products else None
            
            # Calculate data quality score
            summary.data_quality_score = self._calculate_data_quality_score(
                historical_data, cut_events, maintenance_tickets, production_runs
            )
            
            summary.last_updated = datetime.now(timezone.utc)
            
            logger.debug(f"Processed summary for {machine_id} on {target_date} shift {shift}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing summary for {machine_id}: {str(e)}")
            return False
    
    def update_machine_status_cache(self) -> bool:
        """Update real-time machine status cache."""
        logger.info("Updating machine status cache")
        
        try:
            with get_db() as db:
                for machine_id in self.config.MACHINE_IDS:
                    self._update_single_machine_status(db, machine_id)
                
                db.commit()
                logger.info("Successfully updated machine status cache")
                return True
                
        except Exception as e:
            logger.error(f"Error updating machine status cache: {str(e)}")
            return False
    
    def _update_single_machine_status(self, db: Session, machine_id: str) -> None:
        """Update status cache for a single machine."""
        try:
            # Get or create cache entry
            cache = db.query(MachineStatusCache).filter(
                MachineStatusCache.machine_id == machine_id
            ).first()
            
            if not cache:
                cache = MachineStatusCache(machine_id=machine_id)
                db.add(cache)
            
            # Get machine name from historical data
            machine_info = db.query(HistoricalMachineData)\
                           .filter(HistoricalMachineData.machine_id == machine_id)\
                           .first()
            cache.machine_name = machine_info.name if machine_info else f"Machine {machine_id}"
            
            # Get latest cut event
            latest_cut = db.query(CutEvent)\
                          .filter(CutEvent.machine_id == machine_id)\
                          .order_by(CutEvent.timestamp_utc.desc())\
                          .first()
            
            if latest_cut:
                cache.last_activity = latest_cut.timestamp_utc
                cache.last_cut_count = latest_cut.cut_count or 0
                
                # Determine if machine is active (cut within last 10 minutes)
                time_since_last_cut = datetime.now(timezone.utc) - latest_cut.timestamp_utc
                cache.is_active = time_since_last_cut < timedelta(minutes=10)
                cache.current_status = 'active' if cache.is_active else 'idle'
            else:
                cache.is_active = False
                cache.current_status = 'unknown'
            
            # Calculate daily cuts (today)
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_cuts = db.query(func.sum(CutEvent.cut_count))\
                          .filter(
                              CutEvent.machine_id == machine_id,
                              CutEvent.timestamp_utc >= today_start
                          ).scalar()
            cache.daily_cuts = today_cuts or 0
            
            # Get today's utilization from summary
            today_summary = db.query(AnalyticalDataSummary)\
                             .filter(
                                 AnalyticalDataSummary.machine_id == machine_id,
                                 AnalyticalDataSummary.date == today_start.date(),
                                 AnalyticalDataSummary.shift.is_(None)
                             ).first()
            cache.daily_utilization = today_summary.utilization_percentage if today_summary else 0
            
            cache.last_updated = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error updating cache for machine {machine_id}: {str(e)}")
    
    def process_downtime_summaries(self, target_date: Optional[date] = None) -> bool:
        """Process downtime analysis summaries."""
        if target_date is None:
            target_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()
        
        logger.info(f"Processing downtime summaries for {target_date}")
        
        try:
            with get_db() as db:
                start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
                end_time = start_time + timedelta(days=1)
                
                for machine_id in self.config.MACHINE_IDS:
                    # Get downtime events
                    downtime_events = db.query(HistoricalMachineData).filter(
                        HistoricalMachineData.machine_id == machine_id,
                        HistoricalMachineData.start_timestamp >= start_time,
                        HistoricalMachineData.end_timestamp <= end_time,
                        HistoricalMachineData.classification == 'Downtime'
                    ).all()
                    
                    # Group by downtime reason
                    downtime_by_category = {}
                    for event in downtime_events:
                        category = event.downtime_reason_name or 'Unknown'
                        if category not in downtime_by_category:
                            downtime_by_category[category] = []
                        downtime_by_category[category].append(event)
                    
                    # Create summary records
                    for category, events in downtime_by_category.items():
                        summary = db.query(DowntimeSummary).filter(
                            DowntimeSummary.machine_id == machine_id,
                            DowntimeSummary.date == target_date,
                            DowntimeSummary.downtime_category == category
                        ).first()
                        
                        if not summary:
                            summary = DowntimeSummary(
                                machine_id=machine_id,
                                date=target_date,
                                downtime_category=category
                            )
                            db.add(summary)
                        
                        summary.total_downtime_seconds = sum(e.duration_seconds for e in events)
                        summary.event_count = len(events)
                        summary.average_event_duration = summary.total_downtime_seconds / len(events)
                        summary.last_updated = datetime.now(timezone.utc)
                
                db.commit()
                logger.info("Successfully processed downtime summaries")
                return True
                
        except Exception as e:
            logger.error(f"Error processing downtime summaries: {str(e)}")
            return False
    
    def _calculate_data_quality_score(
        self, 
        historical_data: List, 
        cut_events: List, 
        maintenance_tickets: List, 
        production_runs: List
    ) -> float:
        """Calculate a data quality score based on data completeness."""
        score = 1.0
        
        # Reduce score if we have no data
        if not historical_data:
            score -= 0.4
        if not cut_events:
            score -= 0.3
        if not maintenance_tickets and not production_runs:
            score -= 0.2
        
        # Check for data inconsistencies
        if historical_data:
            incomplete_events = [e for e in historical_data if not e.duration_seconds]
            if incomplete_events:
                score -= 0.1 * (len(incomplete_events) / len(historical_data))
        
        return max(score, 0.0)

# Global instance
background_processor = BackgroundDataProcessor()
