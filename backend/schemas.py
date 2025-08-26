import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# --- Pydantic Models (API Schemas) ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    re_password: str # For password confirmation in registration
    role: str = "EMPLOYEE" # Default role

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

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    onboarded: Optional[bool] = None
    # Add other fields that can be updated by the user

class Token(BaseModel):
    """Pydantic model for the authentication token response."""
    access_token: str
    refresh_token: str # Added refresh_token
    token_type: str

class TokenData(BaseModel):
    """Pydantic model for the data encoded within a JWT token."""
    email: Optional[str] = None

# --- Schemas for PLC Cut Events ---
class CutEvent(BaseModel):
    id: int
    machine_id: str
    timestamp_utc: datetime.datetime
    cut_count: Optional[int] = None

    class Config:
        from_attributes = True

# --- Schemas for Operator Terminal (Products & Production Runs) ---
class ProductBase(BaseModel):
    product_name: str
    product_code: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductionRunBase(BaseModel):
    machine_id: str
    product_id: int

class ProductionRunCreate(ProductionRunBase):
    pass

class ProductionRunUpdate(BaseModel):
    status: Optional[str] = None
    scrap_length: float

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
class TicketWorkNoteBase(BaseModel):
    note: str
    author: str

class TicketWorkNoteCreate(TicketWorkNoteBase):
    pass

class TicketWorkNoteBase(BaseModel):
    note: str
    author: str

class TicketWorkNoteCreate(TicketWorkNoteBase):
    pass

class TicketWorkNote(TicketWorkNoteBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class TicketImage(BaseModel):
    id: int
    image_url: str
    caption: Optional[str] = None
    class Config:
        from_attributes = True

class MaintenanceTicketBase(BaseModel):
    incident_category: str
    description: str
    priority: Optional[str] = "Medium"
    machine_id: str
    fourjaw_downtime_id: Optional[str] = None

class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass

class RepairComponentBase(BaseModel):
    component_name: str
    stock_code: Optional[str] = None
    current_stock: int

class RepairComponent(RepairComponentBase):
    id: int
    class Config:
        from_attributes = True

# NEW: Schema for components used in a ticket response
class TicketComponentUsed(BaseModel):
    quantity_used: int
    component: RepairComponent # Use direct reference after RepairComponent is defined

    class Config:
        from_attributes = True

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

class Machine(BaseModel):
    id: str
    name: str

class OeeResponse(BaseModel):
    oee: float
    availability: float
    performance: float
    quality: float

class UtilizationResponse(BaseModel):
    total_time_seconds: float
    productive_uptime_seconds: float
    unproductive_downtime_seconds: float
    productive_downtime_seconds: float
    utilization_percentage: float

class DowntimeEntry(BaseModel):
    name: str
    machine_id: str
    downtime_reason_name: str
    duration_seconds: float
    start_timestamp: datetime.datetime
    end_timestamp: datetime.datetime

class DowntimeAnalysisResponse(BaseModel):
    excessive_downtimes: List[DowntimeEntry]
    recurring_downtime_reasons: dict
