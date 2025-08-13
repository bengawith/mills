import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
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
@app.get("/api/v1/machine-data", tags=["Machine Data"])
async def get_machine_data(
    machine_ids: List[str] = Query(...),
    page_size: int = 1000,
    page: int = 1
):
    from datetime import datetime, timedelta

    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    start_iso = start_time.isoformat().replace('+00:00', 'Z')
    end_iso = end_time.isoformat().replace('+00:00', 'Z')

    try:
        fourjaw_client = FourJaw()
        processor_config = DataProcessorConfig(
            client=fourjaw_client,
            start_time=start_iso,
            end_time=end_iso,
            page_size=page_size,
            page=page,
            machine_ids=machine_ids
        )
        processor = DataProcessor(processor_config)

        processed_data = processor.process_time_entries()

        # You can convert the DataFrame to JSON here if needed
        return {
            "machine_ids": machine_ids,
            "message": "Data processed successfully",
            "row_count": len(processed_data),
            # "data": processed_data.to_dict(orient="records")  # optional
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

