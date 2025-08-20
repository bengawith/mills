from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the new routers
from routers import auth, data, maintenance, inventory, production, events, fourjaw_proxy
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

# --- Include Routers ---
# This adds all the endpoints from your auth.py and data.py files to the main app
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(production.router)
app.include_router(maintenance.router)
app.include_router(inventory.router)
app.include_router(events.router)
app.include_router(fourjaw_proxy.router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


# --- Root Endpoint ---
@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "Mill Dash API is running"}
