from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the new routers
from routers import auth, data
from const.config import Config

# --- Application Setup ---
app = FastAPI(
    title="Mill Dash API",
    description="The backend API for the CSS Support Systems production dashboard.",
    version="0.1.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
# This adds all the endpoints from your auth.py and data.py files to the main app
app.include_router(auth.router)
app.include_router(data.router)


# --- Root Endpoint ---
@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "Mill Dash API is running"}
