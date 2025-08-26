from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
from pydantic import BaseModel

from const.config import config
from fourjaw import DataProcessor
from security import get_current_active_user
from database import get_db # Import the database session dependency
import schemas


router = APIRouter(
    prefix="/api/v1",
    tags=["Machine Data"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/machine-data")
async def get_machine_data(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Fetches and processes time entries for a given list of machines and a time window.
    This endpoint now queries historical data from the database and processes it using DataProcessor.
    Optional filters for shift and day of week are available.
    """
    processor = DataProcessor()
    
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    # Fetch raw data from DB
    df = processor.get_data_from_db(db, start_dt, end_dt, machine_ids)
    
    # Process data (add shift, day_of_week, utilisation_category)
    processed_df = processor.process_data(df)

    if processed_df.empty:
        return [] # Return empty list for empty data

    # Filter by shift and day_of_week if provided
    if shift:
        processed_df = processed_df[processed_df['shift'] == shift.upper()]
    if day_of_week:
        processed_df = processed_df[processed_df['day_of_week'] == day_of_week.upper()]

    return processed_df.to_dict(orient="records")

@router.get("/oee", response_model=schemas.OeeResponse)
async def get_oee(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Calculates Overall Equipment Effectiveness (OEE) for the given filters.
    """
    processor = DataProcessor()
    
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    df = processor.get_data_from_db(db, start_dt, end_dt, machine_ids)
    processed_df = processor.process_data(df)

    if processed_df.empty:
        return schemas.OeeResponse(oee=0, availability=0, performance=0, quality=0) # Return default for empty data

    if shift:
        processed_df = processed_df[processed_df['shift'] == shift.upper()]
    if day_of_week:
        processed_df = processed_df[processed_df['day_of_week'] == day_of_week.upper()]

    oee_data = processor.calculate_oee(processed_df)
    return schemas.OeeResponse(**oee_data)

@router.get("/utilization", response_model=schemas.UtilizationResponse)
async def get_utilization(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Calculates machine utilization for the given filters.
    """
    processor = DataProcessor()
    
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    df = processor.get_data_from_db(db, start_dt, end_dt, machine_ids)
    processed_df = processor.process_data(df)

    if processed_df.empty:
        return schemas.UtilizationResponse(total_time_seconds=0, productive_uptime_seconds=0, unproductive_downtime_seconds=0, productive_downtime_seconds=0, utilization_percentage=0) # Return default for empty data

    if shift:
        processed_df = processed_df[processed_df['shift'] == shift.upper()]
    if day_of_week:
        processed_df = processed_df[processed_df['day_of_week'] == day_of_week.upper()]

    utilization_data = processor.calculate_utilization(processed_df)
    return schemas.UtilizationResponse(**utilization_data)

@router.get("/downtime-analysis", response_model=schemas.DowntimeAnalysisResponse)
async def get_downtime_analysis(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    machine_ids: Optional[List[str]] = Query(None),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    excessive_downtime_threshold_seconds: int = Query(3600),
    db: Session = Depends(get_db)
):
    """
    Analyzes excessive and recurring downtimes for the given filters.
    """
    processor = DataProcessor()
    
    start_dt = datetime.fromisoformat(start_time) if start_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None

    df = processor.get_data_from_db(db, start_dt, end_dt, machine_ids)
    processed_df = processor.process_data(df)

    if processed_df.empty:
        return schemas.DowntimeAnalysisResponse(excessive_downtimes=[], recurring_downtime_reasons={}) # Return default for empty data

    if shift:
        processed_df = processed_df[processed_df['shift'] == shift.upper()]
    if day_of_week:
        processed_df = processed_df[processed_df['day_of_week'] == day_of_week.upper()]
    if machine_ids:
        processed_df = processed_df[processed_df['machine_id'].isin(machine_ids)]

    downtime_data = processor.analyze_downtime(processed_df, excessive_downtime_threshold_seconds)
    return schemas.DowntimeAnalysisResponse(**downtime_data)


@router.get("/machines", response_model=List[schemas.Machine])
async def get_machines():
    """Returns a list of all available machines with their IDs and names."""
    return [{"id": id, "name": name} for id, name in config.MACHINE_ID_MAP.items()]

@router.get("/shifts", response_model=List[str])
async def get_shifts():
    """
    Returns a list of all available shifts.
    """
    return ["DAY", "NIGHT"]

@router.get("/days-of-week", response_model=List[str])
async def get_days_of_week():
    """
    Returns a list of all available days of the week.
    """
    return ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
