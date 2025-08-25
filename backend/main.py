from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# Import the new routers
from routers import auth, data, maintenance, inventory, production, events, fourjaw_proxy, dashboard
from const.config import Config
from database import Base, engine

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


# --- Mount Static Files Directory for Image Uploads ---
# This makes the 'uploads' directory accessible to the frontend
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True) # Ensure the directory exists
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# --- Include Routers ---
# This adds all the endpoints from your auth.py and data.py files to the main app
app.include_router(auth.router, prefix="/auth")
app.include_router(data.router)
app.include_router(production.router)
app.include_router(maintenance.router)
app.include_router(inventory.router)
app.include_router(events.router)
app.include_router(fourjaw_proxy.router)
app.include_router(dashboard.router)

# --- Database Setup ---
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


# --- Root Endpoint ---
@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    print("[DEBUG] Root endpoint hit!")
    return {"status": "Mill Dash API is running"}
