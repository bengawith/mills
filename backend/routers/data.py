from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from fourjaw import DataProcessor, DataProcessorConfig
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Machine Data"],
    # This dependency applies the security check to all endpoints in this router
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/machine-data")
async def get_machine_data(
    start_time: str, 
    end_time: str,
    machine_ids: List[str] = Query(...)
):
    """
    Fetches and processes time entries for a given list of machines and a time window.
    This endpoint is protected and requires authentication.
    """
    try:
        # The DataProcessorConfig and its dependencies are now correctly handled
        processor_config = DataProcessorConfig(
            start_time=start_time,
            end_time=end_time,
            machine_ids=machine_ids
        )
        processor = DataProcessor(config=processor_config)
        
        processed_data = processor.process_time_entries()
        
        # Convert the DataFrame to a JSON-serializable format (list of dicts)
        return processed_data.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
