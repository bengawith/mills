import datetime
from typing import List, Optional
from pydantic import BaseModel

# --- Pydantic Models (API Schemas) ---

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Pydantic model for the authentication token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Pydantic model for the data encoded within a JWT token."""
    username: Optional[str] = None

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
    status: str
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
    priority: str
    machine_id: str
    fourjaw_downtime_id: Optional[str] = None

class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass

class MaintenanceTicket(MaintenanceTicketBase):
    id: int
    logged_time: datetime.datetime
    resolved_time: Optional[datetime.datetime] = None
    status: str
    work_notes: List[TicketWorkNote] = []
    images: List[TicketImage] = []

    class Config:
        from_attributes = True

# --- Schemas for Inventory ---
class RepairComponentBase(BaseModel):
    component_name: str
    stock_code: Optional[str] = None
    current_stock: int

class RepairComponentCreate(RepairComponentBase):
    pass

class RepairComponent(RepairComponentBase):
    id: int
    class Config:
        from_attributes = True


# NEW: Schema for components used in a ticket response
class TicketComponentUsed(BaseModel):
    quantity_used: int
    component: "RepairComponent" # Use string forward reference for nested model

    class Config:
        from_attributes = True

class MaintenanceTicket(MaintenanceTicketBase):
    id: int
    logged_time: datetime.datetime
    resolved_time: Optional[datetime.datetime] = None
    status: str
    work_notes: List[TicketWorkNote] = []
    images: List[TicketImage] = []
    components_used: List[TicketComponentUsed] = [] # <-- ADD THIS LINE

    class Config:
        from_attributes = True

TicketComponentUsed.update_forward_refs()