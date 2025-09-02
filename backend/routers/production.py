from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
import datetime as dt

from sqlalchemy.orm import Session
import schemas
import database_models
from database import get_db
from security import get_current_active_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Production"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)) -> schemas.Product:
    """
    Creates a new product in the database.

    Args:
        product (schemas.ProductCreate): Product creation data.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        schemas.Product: The created product.
    """
    db_product = database_models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.Product]:
    """
    Retrieves a list of all products for frontend dropdowns.

    Args:
        skip (int): Number of records to skip (pagination).
        limit (int): Maximum number of records to return.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        List[schemas.Product]: List of products.
    """
    products = db.query(database_models.Product).offset(skip).limit(limit).all()
    return products

@router.post("/runs", response_model=schemas.ProductionRun, status_code=status.HTTP_201_CREATED)
def start_production_run(run: schemas.ProductionRunCreate, db: Session = Depends(get_db)) -> schemas.ProductionRun:
    """
    Starts a new production run for a machine and product.

    Args:
        run (schemas.ProductionRunCreate): Production run creation data.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        schemas.ProductionRun: The created production run.

    Raises:
        HTTPException: If machine already has an active run.
    """
    active_run = db.query(database_models.ProductionRun).filter(
        database_models.ProductionRun.machine_id == run.machine_id,
        database_models.ProductionRun.status == 'ACTIVE'
    ).first()
    if active_run:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Machine {run.machine_id} already has an active production run."
        )
    db_run = database_models.ProductionRun(**run.dict(), status='ACTIVE')
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

@router.put("/runs/{run_id}/complete", response_model=schemas.ProductionRun)
def complete_production_run(run_id: int, run_update: schemas.ProductionRunUpdate, db: Session = Depends(get_db)) -> schemas.ProductionRun:
    """
    Completes a production run and logs the scrap length.

    Args:
        run_id (int): ID of the production run to complete.
        run_update (schemas.ProductionRunUpdate): Update data for the run.
        db (Session): SQLAlchemy database session (injected).

    Returns:
        schemas.ProductionRun: The completed production run.

    Raises:
        HTTPException: If run not found or already completed.
    """
    db_run = db.query(database_models.ProductionRun).filter(database_models.ProductionRun.id == run_id).first()
    if not db_run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production run not found")
    # Fix: Extract string value from SQLAlchemy column if necessary
    status_value = db_run.status if isinstance(db_run.status, str) else str(db_run.status)
    if status_value == 'COMPLETED':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This run is already completed.")
    db_run.status = 'COMPLETED'
    db_run.scrap_length = run_update.scrap_length
    db_run.end_time = dt.datetime.now(dt.timezone.utc)
    db.commit()
    db.refresh(db_run)
    return db_run
