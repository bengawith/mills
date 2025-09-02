
# ---
# API schemas for request/response validation using Pydantic models.
# Defines the structure of data exchanged via FastAPI endpoints.
# ---

import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# --- Pydantic Models (API Schemas) ---


# --- Authentication Schemas ---
# Login request schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# User creation schema for registration
class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    re_password: str # For password confirmation in registration
    role: str = "EMPLOYEE" # Default role


# User response schema for returning user info to frontend
class UserResponse(BaseModel):
    user_id: int = Field(alias="id") # Map 'id' from DB to 'user_id' for frontend
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    onboarded: bool
    disabled: bool

    class Config:
        from_attributes = True
        populate_by_name = True # Allow population by field name or alias


# User update schema for PATCH/PUT requests
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    onboarded: Optional[bool] = None
    # Add other fields that can be updated by the user


# Authentication token response schema
class Token(BaseModel):
    """Pydantic model for the authentication token response."""
    access_token: str
    refresh_token: str # Added refresh_token
    token_type: str


# JWT token data schema
class TokenData(BaseModel):
    """Pydantic model for the data encoded within a JWT token."""
    email: Optional[str] = None


# --- Schemas for PLC Cut Events ---
# Cut event schema for PLC sensor data
class CutEvent(BaseModel):
    id: int
    machine_id: str
    timestamp_utc: datetime.datetime
    cut_count: Optional[int] = None

    class Config:
        from_attributes = True


# --- Schemas for Operator Terminal (Products & Production Runs) ---
# Product base schema
class ProductBase(BaseModel):
    product_name: str
    product_code: Optional[str] = None


# Product creation schema
class ProductCreate(ProductBase):
    pass


# Product response schema
class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True


# Production run base schema
class ProductionRunBase(BaseModel):
    machine_id: str
    product_id: int


# Production run creation schema
class ProductionRunCreate(ProductionRunBase):
    pass


# Production run update schema
class ProductionRunUpdate(BaseModel):
    status: Optional[str] = None
    scrap_length: float


# Production run response schema
class ProductionRun(ProductionRunBase):
    id: int
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    status: str
    scrap_length: Optional[float] = None
    product: Product # Nest the product details in the response

    class Config:
        from_attributes = True


# --- Schemas for Maintenance Hub ---
# Ticket work note base schema
class TicketWorkNoteBase(BaseModel):
    note: str
    author: str


# Ticket work note creation schema
class TicketWorkNoteCreate(TicketWorkNoteBase):
    pass

class TicketWorkNoteBase(BaseModel):
    note: str
    author: str

class TicketWorkNoteCreate(TicketWorkNoteBase):
    pass


# Ticket work note response schema
class TicketWorkNote(TicketWorkNoteBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True


# Ticket image response schema
class TicketImage(BaseModel):
    id: int
    image_url: str
    caption: Optional[str] = None
    class Config:
        from_attributes = True


# Maintenance ticket base schema
class MaintenanceTicketBase(BaseModel):
    incident_category: str
    description: str
    priority: Optional[str] = "Medium"
    machine_id: str
    fourjaw_downtime_id: Optional[str] = None


# Maintenance ticket creation schema
class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass


# Repair component base schema
class RepairComponentBase(BaseModel):
    component_name: str
    stock_code: Optional[str] = None
    current_stock: int


# Repair component response schema
class RepairComponent(RepairComponentBase):
    id: int
    class Config:
        from_attributes = True


# Schema for components used in a ticket response
class TicketComponentUsed(BaseModel):
    quantity_used: int
    component: RepairComponent # Use direct reference after RepairComponent is defined

    class Config:
        from_attributes = True


# Maintenance ticket response schema
class MaintenanceTicket(MaintenanceTicketBase):
    id: int
    logged_time: datetime.datetime
    resolved_time: Optional[datetime.datetime] = None
    status: str
    work_notes: List[TicketWorkNote] = []
    images: List[TicketImage] = []
    components_used: List[TicketComponentUsed] = []

    class Config:
        from_attributes = True


# Machine response schema
class Machine(BaseModel):
    id: str
    name: str


# OEE (Overall Equipment Effectiveness) response schema
class OeeResponse(BaseModel):
    oee: float
    availability: float
    performance: float
    quality: float


# Utilization response schema
class UtilizationResponse(BaseModel):
    total_time_seconds: float
    productive_uptime_seconds: float
    unproductive_downtime_seconds: float
    productive_downtime_seconds: float
    utilization_percentage: float


# Downtime entry schema for downtime analysis
class DowntimeEntry(BaseModel):
    name: str
    machine_id: str
    downtime_reason_name: str
    duration_seconds: float
    start_timestamp: datetime.datetime
    end_timestamp: datetime.datetime


# Downtime analysis response schema
class DowntimeAnalysisResponse(BaseModel):
    excessive_downtimes: List[DowntimeEntry]
    recurring_downtime_reasons: dict
