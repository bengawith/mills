from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
import shutil
from pathlib import Path
import datetime

# Import your schemas, database models, and database session logic
import schemas
import database_models
from database import get_db # Assuming get_db is your dependency for DB sessions
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1/tickets",
    tags=["Maintenance Tickets"],
    dependencies=[Depends(get_current_active_user)]
)



@router.post("/{ticket_id}/upload-image", response_model=schemas.TicketImage)
def upload_image_for_ticket(ticket_id: int, db: Session = Depends(get_db), file: UploadFile = File(...)):
    """
    Uploads an image and associates it with a maintenance ticket.
    """
    upload_dir = Path("uploads/ticket_images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename to prevent overwrites
    file_extension = Path(file.filename).suffix
    file_path = upload_dir / f"{ticket_id}_{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}{file_extension}"
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create the database record
    image_url = str(file_path)
    db_image = database_models.TicketImage(ticket_id=ticket_id, image_url=image_url)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image


@router.post("/", response_model=schemas.MaintenanceTicket, status_code=status.HTTP_201_CREATED)
def create_maintenance_ticket(ticket: schemas.MaintenanceTicketCreate, db: Session = Depends(get_db)):
    """Creates a new maintenance ticket."""
    db_ticket = database_models.MaintenanceTicket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/", response_model=List[schemas.MaintenanceTicket])
def read_maintenance_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves a list of all maintenance tickets."""
    tickets = db.query(database_models.MaintenanceTicket).order_by(database_models.MaintenanceTicket.logged_time.desc()).offset(skip).limit(limit).all()
    return tickets

@router.get("/{ticket_id}", response_model=schemas.MaintenanceTicket)
def read_maintenance_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed information for a single ticket, including related data.
    """
    db_ticket = db.query(database_models.MaintenanceTicket).options(
        joinedload(database_models.MaintenanceTicket.work_notes),
        joinedload(database_models.MaintenanceTicket.images),
        joinedload(database_models.MaintenanceTicket.components_used).joinedload(database_models.TicketComponentUsed.component)
    ).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@router.put("/{ticket_id}", response_model=schemas.MaintenanceTicket)
def update_maintenance_ticket(ticket_id: int, status: str, db: Session = Depends(get_db)):
    """
    Updates a ticket's status. If status is 'Resolved', sets the resolved_time.
    If status is not 'Resolved', resolved_time is set to None.
    """
    db_ticket = db.query(database_models.MaintenanceTicket).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db_ticket.status = status
    if status == "Resolved":
        db_ticket.resolved_time = datetime.datetime.now(datetime.timezone.utc)
    else:
        db_ticket.resolved_time = None
        
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.post("/{ticket_id}/notes", response_model=schemas.TicketWorkNote)
def create_work_note_for_ticket(ticket_id: int, note: schemas.TicketWorkNoteCreate, db: Session = Depends(get_db)):
    """Adds a new work note to a specific ticket."""
    db_ticket = db.query(database_models.MaintenanceTicket).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_note = database_models.TicketWorkNote(**note.dict(), ticket_id=ticket_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.post("/{ticket_id}/components", response_model=schemas.MaintenanceTicket)
def add_component_to_ticket(ticket_id: int, component_id: int, quantity_used: int, db: Session = Depends(get_db)):
    """Associates a repair component with a maintenance ticket."""
    db_ticket = db.query(database_models.MaintenanceTicket).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db_component = db.query(database_models.RepairComponent).filter(database_models.RepairComponent.id == component_id).first()
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Decrement stock
    if db_component.current_stock < quantity_used:
        raise HTTPException(status_code=400, detail="Not enough components in stock")
    db_component.current_stock -= quantity_used

    # Create the link table entry
    ticket_component = database_models.TicketComponentUsed(
        ticket_id=ticket_id,
        component_id=component_id,
        quantity_used=quantity_used
    )
    db.add(ticket_component)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket