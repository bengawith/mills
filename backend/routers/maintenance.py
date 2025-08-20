from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import shutil
from pathlib import Path

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


@router.post("/", response_model=schemas.MaintenanceTicket, status_code=status.HTTP_201_CREATED)
def create_maintenance_ticket(ticket: schemas.MaintenanceTicketCreate, db: Session = Depends(get_db)):
    """
    Creates a new maintenance ticket.
    """
    db_ticket = database_models.MaintenanceTicket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get("/", response_model=List[schemas.MaintenanceTicket])
def read_maintenance_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all maintenance tickets.
    """
    tickets = db.query(database_models.MaintenanceTicket).offset(skip).limit(limit).all()
    return tickets


@router.get("/{ticket_id}", response_model=schemas.MaintenanceTicket)
def read_maintenance_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed information for a single ticket.
    """
    db_ticket = db.query(database_models.MaintenanceTicket).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket


@router.post("/{ticket_id}/notes", response_model=schemas.TicketWorkNote)
def create_work_note_for_ticket(ticket_id: int, note: schemas.TicketWorkNoteCreate, db: Session = Depends(get_db)):
    """
    Adds a new work note to a specific ticket.
    """
    db_ticket = db.query(database_models.MaintenanceTicket).filter(database_models.MaintenanceTicket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_note = database_models.TicketWorkNote(**note.dict(), ticket_id=ticket_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.post("/{ticket_id}/upload-image", response_model=schemas.TicketImage)
def upload_image_for_ticket(ticket_id: int, db: Session = Depends(get_db), file: UploadFile = File(...)):
    """
    Uploads an image and associates it with a maintenance ticket.
    """
    # Define a secure path to save the uploaded files
    # In production, this should point to a persistent volume or cloud storage
    upload_dir = Path("uploads/ticket_images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename to prevent overwrites
    file_extension = Path(file.filename).suffix
    file_path = upload_dir / f"{ticket_id}_{int(datetime.now().timestamp())}{file_extension}"
    
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