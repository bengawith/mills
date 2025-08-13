import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import your existing logic
from fourjaw import FourJaw
from fourjaw import DataProcessor, DataProcessorConfig
from const.config import Config

# --- Application Setup ---
app: FastAPI = FastAPI(
    title="Mill Dash API",
    description="The backend API for the CSS Support Systems production dashboard.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "Mill Dash API is running"}


# --- Placeholder for future data endpoint ---
# We will build this out properly later. This shows how it will work.
@app.get("/api/v1/machine-data/{machine_id}", tags=["Machine Data"])
async def get_machine_data(machine_id: list[str]):
    """
    A placeholder endpoint to fetch processed data for a single machine.
    
    This demonstrates how we will use the existing DataProcessor logic.
    """
    # In a real scenario, we would pass start and end times from the frontend.
    from datetime import datetime, timedelta
    
    # For now, we'll just use a fixed window for the example.
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    start_iso = start_time.isoformat().replace('+00:00', 'Z')
    end_iso = end_time.isoformat().replace('+00:00', 'Z')
    page_size = 1000

    try:
        # Initialize your FourJaw client and processor inside the endpoint
        fourjaw_client = FourJaw()
        processor_config = DataProcessorConfig(
            client=fourjaw_client,
            start_time=start_iso,
            end_time=end_iso,
            page_size=page_size,
            machine_ids=machine_id
        )
        processor = DataProcessor(processor_config)
        
        # This will call your existing logic
        # Note: We'd need to adapt process_time_entries to handle a single machine ID
        # For now, this illustrates the concept.
        
        # Faking a response for now
        # processed_data = processor.process_time_entries(start_iso, end_iso)
        
        return {"machine_id": machine_id, "message": "This endpoint is a work in progress. Data will be returned here."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

