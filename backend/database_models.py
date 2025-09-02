
# Standard library import for timestamps
import datetime
# SQLAlchemy imports for ORM model definitions
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

# Import the declarative base from database.py
from database import Base


# --- Core Application Models ---
# User model: stores user account and profile information
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Unique email for login
    first_name = Column(String)                      # User's first name
    last_name = Column(String)                       # User's last name
    hashed_password = Column(String)                 # Hashed password for security
    role = Column(String, default="EMPLOYEE")      # Role: ADMIN or EMPLOYEE
    onboarded = Column(Boolean, default=False)       # Has the user completed onboarding?
    disabled = Column(Boolean, default=False)        # Is the user account disabled?


# HistoricalMachineData: stores historical records of machine activity and downtime
class HistoricalMachineData(Base):
    __tablename__ = "historical_machine_data"
    id = Column(String, primary_key=True, index=True)         # Unique event ID
    name = Column(String)                                     # Event name
    machine_id = Column(String, index=True)                   # Machine identifier
    downtime_reason_name = Column(String, nullable=True)      # Reason for downtime
    end_timestamp = Column(DateTime(timezone=True))           # End time of event
    start_timestamp = Column(DateTime(timezone=True))         # Start time of event
    productivity = Column(String)                             # Productivity metric
    classification = Column(String)                           # Classification of event
    duration_seconds = Column(Float)                          # Duration in seconds
    shift = Column(String)                                    # Shift name
    day_of_week = Column(String)                              # Day of week
    utilisation_category = Column(String)                     # Utilization category


# --- Models for PLC Cut Sensor ---
# CutEvent: records cut events from PLC sensors
class CutEvent(Base):
    __tablename__ = 'cut_events'
    id = Column(Integer, primary_key=True, index=True)        # Unique cut event ID
    machine_id = Column(String, index=True, nullable=False)   # Machine identifier
    timestamp_utc = Column(DateTime, nullable=False)          # UTC timestamp of cut
    cut_count = Column(Integer)                               # Number of cuts


# --- Models for Operator Terminal (Product & Scrap) ---
# Product: stores product information
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)        # Unique product ID
    product_name = Column(String, unique=True, nullable=False)# Product name
    product_code = Column(String, unique=True)                # Product code
    # Relationship to production runs
    production_runs = relationship("ProductionRun", back_populates="product")


# ProductionRun: records each run of a product on a machine
class ProductionRun(Base):
    __tablename__ = 'production_runs'
    id = Column(Integer, primary_key=True, index=True)        # Unique run ID
    machine_id = Column(String, index=True, nullable=False)   # Machine identifier
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False) # Product reference
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)) # Start time
    end_time = Column(DateTime, nullable=True)                # End time
    status = Column(String, default='ACTIVE')                 # Run status
    scrap_length = Column(Float, nullable=True)               # Scrap length

    product = relationship("Product", back_populates="production_runs") # Relationship to product



# --- Models for Maintenance Hub ---
# MaintenanceTicket: records maintenance incidents and their details
class MaintenanceTicket(Base):
    __tablename__ = 'maintenance_tickets'
    id = Column(Integer, primary_key=True, index=True)        # Unique ticket ID
    logged_time = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) # When ticket was logged
    resolved_time = Column(DateTime, nullable=True)           # When ticket was resolved
    incident_category = Column(String, nullable=False)        # Category of incident
    description = Column(Text, nullable=False)                # Description of issue
    priority = Column(String, default='Medium')               # Priority level
    status = Column(String, default='Open', index=True)       # Status: Open, Closed, etc.
    fourjaw_downtime_id = Column(String, nullable=True, index=True) # Related downtime event
    machine_id = Column(String, nullable=False, index=True)   # Machine identifier

    # Relationships to other tables
    work_notes = relationship("TicketWorkNote", back_populates="ticket")
    images = relationship("TicketImage", back_populates="ticket")
    components_used = relationship("TicketComponentUsed", back_populates="ticket")


# TicketWorkNote: stores notes added to maintenance tickets
class TicketWorkNote(Base):
    __tablename__ = 'ticket_work_notes'
    id = Column(Integer, primary_key=True, index=True)        # Unique note ID
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False) # Ticket reference
    note = Column(Text, nullable=False)                       # Note text
    author = Column(String)                                   # Author of note
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # Timestamp

    ticket = relationship("MaintenanceTicket", back_populates="work_notes") # Relationship to ticket


# RepairComponent: stores information about repair components
class RepairComponent(Base):
    __tablename__ = 'repair_components'
    id = Column(Integer, primary_key=True, index=True)        # Unique component ID
    component_name = Column(String, unique=True, nullable=False) # Name of component
    stock_code = Column(String, unique=True)                  # Stock code
    current_stock = Column(Integer, default=0)                # Current stock level

    tickets_used_on = relationship("TicketComponentUsed", back_populates="component") # Relationship to tickets

# TicketImage: stores images attached to maintenance tickets
class TicketImage(Base):
    __tablename__ = 'ticket_images'
    id = Column(Integer, primary_key=True, index=True)        # Unique image ID
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False) # Ticket reference
    image_url = Column(String, nullable=False)                # Path/URL to image file
    uploaded_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) # Upload timestamp
    caption = Column(String, nullable=True)                   # Optional caption

    ticket = relationship("MaintenanceTicket", back_populates="images") # Relationship to ticket

# TicketComponentUsed: records which components were used on which tickets
class TicketComponentUsed(Base):
    __tablename__ = 'ticket_components_used'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('maintenance_tickets.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('repair_components.id'), nullable=False)
    quantity_used = Column(Integer, default=1)
    
    ticket = relationship("MaintenanceTicket", back_populates="components_used")
    component = relationship("RepairComponent", back_populates="tickets_used_on")

# --- Summary Tables for Background Processing ---
class AnalyticalDataSummary(Base):
    __tablename__ = 'analytical_data_summary'
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    shift = Column(String, nullable=True, index=True)
    day_of_week = Column(String, nullable=True)
    
    # Aggregated metrics
    total_events = Column(Integer, default=0)
    productive_time_seconds = Column(Float, default=0)
    downtime_seconds = Column(Float, default=0)
    setup_time_seconds = Column(Float, default=0)
    total_cuts = Column(Integer, default=0)
    
    # Calculated metrics
    utilization_percentage = Column(Float, default=0)
    oee_percentage = Column(Float, default=0)
    availability_percentage = Column(Float, default=0)
    performance_percentage = Column(Float, default=0)
    quality_percentage = Column(Float, default=0)
    
    # Maintenance data
    maintenance_tickets_count = Column(Integer, default=0)
    critical_tickets_count = Column(Integer, default=0)
    
    # Production data
    production_runs_count = Column(Integer, default=0)
    products_produced = Column(String, nullable=True)  # JSON list
    
    # Metadata
    last_updated = Column(DateTime(timezone=True), nullable=False)
    data_quality_score = Column(Float, default=1.0)

class MachineStatusCache(Base):
    __tablename__ = 'machine_status_cache'
    
    machine_id = Column(String, primary_key=True)
    machine_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    current_status = Column(String, default='unknown')  # active, idle, down, maintenance
    last_cut_count = Column(Integer, default=0)
    daily_cuts = Column(Integer, default=0)
    daily_utilization = Column(Float, default=0)
    last_updated = Column(DateTime(timezone=True), nullable=False)

class DowntimeSummary(Base):
    __tablename__ = 'downtime_summary'
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    downtime_category = Column(String, nullable=False, index=True)
    total_downtime_seconds = Column(Float, default=0)
    event_count = Column(Integer, default=0)
    average_event_duration = Column(Float, default=0)
    last_updated = Column(DateTime(timezone=True), nullable=False)
