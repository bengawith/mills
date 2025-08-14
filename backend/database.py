import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_secure_password") # Default for development
POSTGRES_DB = os.getenv("POSTGRES_DB", "mill_dash_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean

class MillData(Base):
    __tablename__ = "mill_data"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    machine_id = Column(String, index=True)
    downtime_reason_name = Column(String)
    end_timestamp = Column(DateTime(timezone=True))
    start_timestamp = Column(DateTime(timezone=True))
    productivity = Column(String)
    classification = Column(String)
    duration_seconds = Column(Float)
    shift = Column(String)
    day_of_week = Column(String)
    utilisation_category = Column(String)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
