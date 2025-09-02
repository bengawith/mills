"""
Machine data and analytics service layer.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta
import pandas as pd
import logging

from services.base_service import BaseService
from database_models import HistoricalMachineData, CutEvent
from fourjaw.data_processor import DataProcessor
from const.config import config

logger = logging.getLogger(__name__)

class MachineDataService(BaseService):
    """
    Service class for machine data operations and analytics.
    Provides methods for fetching, processing, and analyzing machine data using pandas and SQLAlchemy.
    Inherits from BaseService for common CRUD operations.
    """
    
    def __init__(self) -> None:
        """
        Initialize MachineDataService with HistoricalMachineData as the model and a DataProcessor instance.
        """
        super().__init__(HistoricalMachineData)
        self.data_processor = DataProcessor()
    
    def get_machine_data(
        self, 
        db: Session, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        machine_ids: Optional[List[str]] = None,
        shift: Optional[str] = None,
        day_of_week: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get machine data with filtering options.
        
        Args:
            db (Session): SQLAlchemy database session.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
            shift (Optional[str]): Shift name to filter.
            day_of_week (Optional[str]): Day of week to filter.
        
        Returns:
            pd.DataFrame: Processed machine data as a pandas DataFrame.
        """
        try:
            # Fetch raw data from DB using data processor
            df = self.data_processor.get_data_from_db(db, start_time, end_time, machine_ids)
            
            # Process data (add shift, day_of_week, utilisation_category)
            processed_df = self.data_processor.process_data(df)
            
            # Apply additional filters
            if shift and not processed_df.empty:
                processed_df = processed_df[processed_df['shift'] == shift]
            
            if day_of_week and not processed_df.empty:
                processed_df = processed_df[processed_df['day_of_week'] == day_of_week]
            
            return processed_df
        except Exception as e:
            logger.error(f"Error fetching machine data: {str(e)}")
            raise
    
    def calculate_oee(
        self,
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        machine_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate Overall Equipment Effectiveness (OEE).
        
        Args:
            db (Session): SQLAlchemy database session.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
        
        Returns:
            Dict[str, Any]: Dictionary with OEE metrics.
        """
        try:
            df = self.get_machine_data(db, start_time, end_time, machine_ids)
            return self.data_processor.calculate_oee(df)
        except Exception as e:
            logger.error(f"Error calculating OEE: {str(e)}")
            raise
    
    def get_utilization_data(
        self,
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        machine_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get machine utilization breakdown.
        
        Args:
            db (Session): SQLAlchemy database session.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
        
        Returns:
            Dict[str, Any]: Dictionary with utilization breakdown.
        """
        try:
            df = self.get_machine_data(db, start_time, end_time, machine_ids)
            return self.data_processor.calculate_utilization(df)
        except Exception as e:
            logger.error(f"Error calculating utilization: {str(e)}")
            raise
    
    def get_downtime_analysis(
        self,
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        machine_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get downtime analysis data.
        
        Args:
            db (Session): SQLAlchemy database session.
            start_time (Optional[datetime]): Start of time range (UTC).
            end_time (Optional[datetime]): End of time range (UTC).
            machine_ids (Optional[List[str]]): List of machine IDs to filter.
        
        Returns:
            Dict[str, Any]: Dictionary with downtime analysis results.
        """
        try:
            df = self.get_machine_data(db, start_time, end_time, machine_ids)
            # Note: calculate_downtime_analysis may not exist, use analyze_downtime from DataProcessor.
            return self.data_processor.analyze_downtime(df)
        except Exception as e:
            logger.error(f"Error calculating downtime analysis: {str(e)}")
            raise
    
    def get_machines_list(self) -> List[Dict[str, str]]:
        """
        Get list of available machines.
        
        Returns:
            List[Dict[str, str]]: List of machine info dictionaries.
        """
        try:
            return [
                {"id": machine_id, "name": name} 
                for machine_id, name in config.MACHINE_ID_MAP.items()
            ]
        except Exception as e:
            logger.error(f"Error getting machines list: {str(e)}")
            raise
    
    def get_latest_timestamp(self, db: Session, machine_id: str) -> Optional[datetime]:
        """Get the latest timestamp for a specific machine."""
        try:
            latest = db.query(HistoricalMachineData.end_timestamp)\
                     .filter(HistoricalMachineData.machine_id == machine_id)\
                     .order_by(HistoricalMachineData.end_timestamp.desc())\
                     .first()
            
            if latest and latest[0]:
                timestamp = latest[0]
                # Ensure the timestamp is timezone-aware
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                return timestamp
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting latest timestamp for machine {machine_id}: {str(e)}")
            raise

class CutEventService(BaseService):
    """Service class for cut event operations."""
    
    def __init__(self):
        super().__init__(CutEvent)
    
    def create_cut_event(self, db: Session, event_data: Dict[str, Any]) -> CutEvent:
        """Create a new cut event."""
        try:
            return self.create(db, event_data)
        except SQLAlchemyError as e:
            logger.error(f"Error creating cut event: {str(e)}")
            raise
    
    def get_events_by_machine(
        self, 
        db: Session, 
        machine_id: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[CutEvent]:
        """Get cut events for a specific machine within a time range."""
        try:
            query = db.query(CutEvent).filter(CutEvent.machine_id == machine_id)
            
            if start_time:
                query = query.filter(CutEvent.timestamp_utc >= start_time)
            
            if end_time:
                query = query.filter(CutEvent.timestamp_utc <= end_time)
            
            return query.order_by(CutEvent.timestamp_utc.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching cut events for machine {machine_id}: {str(e)}")
            raise
    
    def get_daily_cut_count(
        self, 
        db: Session, 
        machine_id: str, 
        date: datetime
    ) -> int:
        """Get total cut count for a specific machine on a specific date."""
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            result = db.query(CutEvent.cut_count)\
                      .filter(CutEvent.machine_id == machine_id)\
                      .filter(CutEvent.timestamp_utc >= start_of_day)\
                      .filter(CutEvent.timestamp_utc < end_of_day)\
                      .all()
            
            return sum(count[0] for count in result if count[0] is not None)
        except SQLAlchemyError as e:
            logger.error(f"Error calculating daily cut count for machine {machine_id}: {str(e)}")
            raise
