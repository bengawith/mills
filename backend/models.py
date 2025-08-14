from pydantic import BaseModel
from typing import Optional

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str


class UserResponse(BaseModel):
    username: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool | None = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Pydantic model for the authentication token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Pydantic model for the data encoded within a JWT token."""
    username: Optional[str] = None


class HistoricalMachineData(Base):
    __tablename__ = "historical_machine_data"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    machine_id = Column(String)
    downtime_reason_name = Column(String, nullable=True)
    end_timestamp = Column(DateTime(timezone=True))
    start_timestamp = Column(DateTime(timezone=True))
    productivity = Column(String)
    classification = Column(String)
    duration_seconds = Column(Float)
    shift = Column(String)
    day_of_week = Column(String)
    utilisation_category = Column(String)

