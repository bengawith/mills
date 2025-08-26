from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import traceback

# Import the routers
from routers import auth, data, maintenance, inventory, production, events, fourjaw_proxy, dashboard, database, dashboard_optimized
from const.config import config
from database import Base, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Application Setup ---
app = FastAPI(
    title="Mill Dash API",
    description="The backend API for the CSS Support Systems production dashboard.",
    version="0.2.0",
)

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "type": type(exc).__name__
        }
    )

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount Static Files Directory for Image Uploads ---
# This makes the 'uploads' directory accessible to the frontend
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True) # Ensure the directory exists
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# --- Include Routers ---
# This adds all the endpoints from your router files to the main app
app.include_router(auth.router, prefix="/auth")
app.include_router(data.router)
app.include_router(production.router)
app.include_router(maintenance.router)
app.include_router(inventory.router)
app.include_router(events.router)
app.include_router(fourjaw_proxy.router)
app.include_router(dashboard.router)
app.include_router(dashboard_optimized.router)
app.include_router(database.router)

# --- Database Setup ---
@app.on_event("startup")
async def startup_event():
    try:
        # Create all database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        logger.info(f"Application started successfully with SQLite database")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

# --- Root Endpoint ---
@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    print("[DEBUG] Root endpoint hit!")
    return {"status": "Mill Dash API is running"}
