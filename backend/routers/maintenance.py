from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
