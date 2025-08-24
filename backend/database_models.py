import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base

# --- Core Application Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="EMPLOYEE") # ADMIN or EMPLOYEE
    onboarded = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)

class HistoricalMachineData(Base):
    __tablename__ = "historical_machine_data"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    machine_id = Column(String, index=True)
    downtime_reason_name = Column(String, nullable=True)
    end_timestamp = Column(DateTime(timezone=True))
    start_timestamp = Column(DateTime(timezone=True))
    productivity = Column(String)
    classification = Column(String)
    duration_seconds = Column(Float)
    shift = Column(String)
    day_of_week = Column(String)
    utilisation_category = Column(String)

# --- Models for PLC Cut Sensor ---
class CutEvent(Base):
    __tablename__ = 'cut_events'
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)
    cut_count = Column(Integer)

# --- Models for Operator Terminal (Product & Scrap) ---
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True, nullable=False)
    product_code = Column(String, unique=True)
    
    production_runs = relationship("ProductionRun", back_populates="product")

class ProductionRun(Base):
    __tablename__ = 'production_runs'
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default='ACTIVE') # e.g., ACTIVE, COMPLETED
    scrap_length = Column(Float, nullable=True)

    product = relationship("Product", back_populates="production_runs")


# --- Models for Maintenance Hub ---
class MaintenanceTicket(Base):
    __tablename__ = 'maintenance_tickets'
    id = Column(Integer, primary_key=True, index=True)
    logged_time = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_time = Column(DateTime, nullable=True)
    incident_category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default='Medium')
    status = Column(String, default='Open', index=True)
    fourjaw_downtime_id = Column(String, nullable=True, index=True)
    machine_id = Column(String, nullable=False, index=True)

    work_notes = relationship("TicketWorkNote", back_populates="ticket")
    images = relationship("TicketImage", back_populates="ticket")
    components_used = relationship("TicketComponentUsed", back_populates="ticket")

class TicketWorkNote(Base):
    __tablename__ = 'ticket_work_notes'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False)
    note = Column(Text, nullable=False)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ticket = relationship("MaintenanceTicket", back_populates="work_notes")

class RepairComponent(Base):
    __tablename__ = 'repair_components'
    id = Column(Integer, primary_key=True, index=True)
    component_name = Column(String, unique=True, nullable=False)
    stock_code = Column(String, unique=True)
    current_stock = Column(Integer, default=0)

    tickets_used_on = relationship("TicketComponentUsed", back_populates="component")

class TicketImage(Base):
    __tablename__ = 'ticket_images'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False)
    image_url = Column(String, nullable=False) # This will store the path/URL to the image file
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    caption = Column(String, nullable=True)

    ticket = relationship("MaintenanceTicket", back_populates="images")
    
class TicketComponentUsed(Base):
    __tablename__ = 'ticket_components_used'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('repair_components.id'), nullable=False)
    quantity_used = Column(Integer, default=1)
    
    ticket = relationship("MaintenanceTicket", back_populates="components_used")
    component = relationship("RepairComponent", back_populates="tickets_used_on")