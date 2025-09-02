from typing import List
from fastapi import APIRouter, Depends, Query
import datetime as dt
from sqlalchemy.orm import Session

import schemas
import database_models
from database import get_db
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Events"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/cuts", response_model=List[schemas.CutEvent])
def get_cut_events(
    start_time: dt.datetime,
    end_time: dt.datetime,
    machine_ids: List[str] = Query(...),
    db: Session = Depends(get_db)
) -> List[schemas.CutEvent]:
    """
    Retrieves a list of cut events for given machines within a time window.

    Args:
        start_time (dt.datetime): Start of time window (UTC).
        end_time (dt.datetime): End of time window (UTC).
        machine_ids (List[str]): List of machine IDs to filter.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        List[schemas.CutEvent]: List of cut event records.
    """
    events = db.query(database_models.CutEvent).filter(
        database_models.CutEvent.machine_id.in_(machine_ids),
        database_models.CutEvent.timestamp_utc >= start_time,
        database_models.CutEvent.timestamp_utc <= end_time
    ).order_by(database_models.CutEvent.timestamp_utc).all()
    return events
