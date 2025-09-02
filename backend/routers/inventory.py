from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import schemas
import database_models
from database import get_db
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/components", response_model=schemas.RepairComponent, status_code=status.HTTP_201_CREATED)
def create_repair_component(component: schemas.RepairComponent, db: Session = Depends(get_db)) -> schemas.RepairComponent:
    """
    Adds a new repair component to the inventory.

    Args:
        component (schemas.RepairComponent): Repair component data.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        schemas.RepairComponent: The created repair component.
    """
    db_component = database_models.RepairComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component

@router.get("/components", response_model=List[schemas.RepairComponent])
def read_repair_components(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.RepairComponent]:
    """
    Retrieves a list of all repair components.

    Args:
        skip (int): Number of records to skip (pagination).
        limit (int): Maximum number of records to return.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        List[schemas.RepairComponent]: List of repair components.
    """
    components = db.query(database_models.RepairComponent).offset(skip).limit(limit).all()
    return components
