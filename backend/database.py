
# Standard library imports
import os
from pathlib import Path
# SQLAlchemy imports for ORM and database connection
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# --- SQLite Configuration ---
# Get database directory and name from environment variables, with defaults
DATABASE_DIR = os.getenv("DATABASE_DIR", "data")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mill_dash.db")

# Ensure the database directory exists before connecting
Path(DATABASE_DIR).mkdir(exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# --- SQLAlchemy Engine Creation ---
# Create the database engine with optimized settings for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Allow SQLite to be used across threads
        "timeout": 30,  # 30 second timeout for database operations
    },
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
)


# --- SQLite PRAGMA Settings ---
# Enable foreign key constraints and optimize SQLite for concurrency and performance
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")           # Enforce foreign key constraints
    cursor.execute("PRAGMA journal_mode=WAL")          # Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA synchronous=NORMAL")        # Balance between safety and speed
    cursor.execute("PRAGMA cache_size=1000")           # Increase cache size
    cursor.execute("PRAGMA temp_store=MEMORY")         # Store temp tables in memory
    cursor.close()


# --- Session and Base Setup ---
# Create a session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# --- Dependency for FastAPI Routes ---
def get_db():
    """
    Dependency for FastAPI routes to provide a database session.
    Ensures the session is closed after use.
    Usage: `Depends(get_db)` in route functions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
