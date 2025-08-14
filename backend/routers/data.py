from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from fourjaw import DataProcessor, DataProcessorConfig
from security import get_current_active_user
from database import get_db # Import the database session dependency
from models import HistoricalMachineData # Import the HistoricalMachineData model

router = APIRouter(
    prefix="/api/v1",
    tags=["Machine Data"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/machine-data")
async def get_machine_data(
    start_time: str,
    end_time: str,
    machine_ids: List[str] = Query(...),
    shift: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    db: Session = Depends(get_db) # Inject database session
):
    """
    Fetches and processes time entries for a given list of machines and a time window.
    This endpoint now queries historical data from the database.
    Optional filters for shift and day of week are available.
    """
    try:
        # Convert string timestamps to datetime objects
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # Build query to fetch data from HistoricalMachineData table
        query = db.query(HistoricalMachineData).filter(
            HistoricalMachineData.start_timestamp >= start_dt,
            HistoricalMachineData.end_timestamp <= end_dt,
            HistoricalMachineData.machine_id.in_(machine_ids)
        )

        if shift:
            query = query.filter(HistoricalMachineData.shift == shift)
        if day_of_week:
            query = query.filter(HistoricalMachineData.day_of_week == day_of_week)

        # Execute query
        historical_data = query.all()

        # Convert SQLAlchemy objects to dictionaries for JSON response
        # This is a simplified conversion; in a larger app, consider Pydantic models for response
        response_data = []
        for item in historical_data:
            response_data.append({
                "id": item.id,
                "name": item.name,
                "machine_id": item.machine_id,
                "downtime_reason_name": item.downtime_reason_name,
                "start_timestamp": item.start_timestamp.isoformat(),
                "end_timestamp": item.end_timestamp.isoformat(),
                "productivity": item.productivity,
                "classification": item.classification,
                "duration_seconds": item.duration_seconds,
                "shift": item.shift,
                "day_of_week": item.day_of_week,
                "utilisation_category": item.utilisation_category
            })
        
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))