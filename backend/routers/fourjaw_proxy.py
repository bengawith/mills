from typing import List
from fastapi import APIRouter, Depends, Query
import datetime as dt
from sqlalchemy.orm import Session

from fourjaw import FourJaw
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1/fourjaw",
    tags=["FourJaw Proxy"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/downtimes")
def get_recent_downtimes_for_machine(
    machine_id: str,
    start_time: dt.datetime,
    end_time: dt.datetime
):
    """
    Fetches recent downtime events directly from the FourJaw API for a specific machine.
    This is used to populate the dropdown when logging a new maintenance ticket.
    """
    api = FourJaw()
    try:
        response = api.get_status_periods(
            start_time=start_time.isoformat().replace('+00:00', 'Z'),
            end_time=end_time.isoformat().replace('+00:00', 'Z'),
            machine_ids=machine_id
        )
        
        # Filter for only downtime events
        if response and 'items' in response:
            downtimes = [
                item for item in response['items'] 
                if item.get('classification') == 'DOWNTIME'
            ]
            return downtimes
        return []
    except Exception as e:
        return {"error": str(e)}
