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
def create_repair_component(component: schemas.RepairComponent, db: Session = Depends(get_db)):
    """
    Adds a new repair component to the inventory.
    """
    db_component = database_models.RepairComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component

@router.get("/components", response_model=List[schemas.RepairComponent])
def read_repair_components(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all repair components.
    """
    components = db.query(database_models.RepairComponent).offset(skip).limit(limit).all()
    return components
