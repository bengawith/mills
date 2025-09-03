
# FastAPI imports for building the web API
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
# Standard library imports for logging and error handling
import logging
import traceback


# Import all routers (API endpoints) for different modules
from routers import analytics, dashboard
from routers import (
    auth, maintenance, inventory, events, 
    fourjaw_proxy, websocket
)
# Import configuration and database setup
from const.config import config
from database import Base, engine


# --- Logging Configuration ---
# Set up logging for the application to track events and errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# --- Application Setup ---
# Create the FastAPI app instance with metadata
app = FastAPI(
    title="Mill Dash API",
    description="The backend API for the CSS Support Systems production dashboard.",
    version="0.2.0",
)


# --- Global Exception Handler ---
# Catches all unhandled exceptions and returns a standardized error response
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    # Return a generic error message to the client
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "type": type(exc).__name__
        }
    )


# --- CORS Middleware ---
# Enables Cross-Origin Resource Sharing for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Mount Static Files Directory for Image Uploads ---
# Exposes the 'uploads' directory for serving static files (e.g., images)
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True) # Ensure the directory exists
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# --- Include Routers ---
# Registers all API endpoint routers with the FastAPI app
app.include_router(auth.router, prefix="/auth")  # Authentication endpoints
app.include_router(maintenance.router)            # Maintenance endpoints
app.include_router(inventory.router)              # Inventory endpoints
app.include_router(events.router)                 # Event endpoints
app.include_router(fourjaw_proxy.router)          # Fourjaw proxy endpoints
app.include_router(dashboard.router)              # Dashboard endpoints
app.include_router(analytics.router)              # Analytics endpoints
app.include_router(websocket.router, prefix="/api/v1")  # WebSocket endpoints for real-time updates


# --- Database Setup ---
# FastAPI startup event: initializes database tables
@app.on_event("startup")
async def startup_event():
    try:
        # Create all database tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        logger.info(f"Application started successfully with SQLite database")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# FastAPI shutdown event: logs shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")


# --- Root Endpoint ---
# Health check endpoint for API status
@app.get("/", tags=["Status"])
async def read_root():
    """
    A simple health check endpoint to confirm the API is running.
    Returns a status message for monitoring and debugging.
    """
    print("[DEBUG] Root endpoint hit!")
    return {"status": "Mill Dash API is running"}
