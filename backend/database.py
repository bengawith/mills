import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# SQLite Configuration
DATABASE_DIR = os.getenv("DATABASE_DIR", "data")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mill_dash.db")

# Ensure the database directory exists
Path(DATABASE_DIR).mkdir(exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with optimized settings for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Allow SQLite to be used across threads
        "timeout": 30,  # 30 second timeout for database operations
    },
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
)

# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
    cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
    cursor.execute("PRAGMA cache_size=1000")  # Increase cache size
    cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
