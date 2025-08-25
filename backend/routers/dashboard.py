from typing import List, Optional
from fastapi import APIRouter, Depends, Query
import datetime as dt
from sqlalchemy.orm import Session
import pandas as pd

import schemas
import database_models
from database import get_db
from security import get_current_active_user
from const.config import Config


router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard Analytics"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/analytical-data")
def get_analytical_data(
    start_time: dt.datetime,
    end_time: dt.datetime,
    machine_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Fetches and correlates data from FourJaw, Production Runs, and Maintenance Tickets
    to provide a single, enriched dataset for dashboard visualizations.
    """
    # 1. Fetch FourJaw Data (HistoricalMachineData)
    if machine_ids is None:
        machine_ids = Config.MACHINE_IDS
    fourjaw_query = db.query(database_models.HistoricalMachineData).filter(
        database_models.HistoricalMachineData.machine_id.in_(machine_ids),
        database_models.HistoricalMachineData.start_timestamp <= end_time,
        database_models.HistoricalMachineData.end_timestamp >= start_time
    )
    fourjaw_df = pd.read_sql(fourjaw_query.statement, db.bind)

    if fourjaw_df.empty:
        return []

    # 2. Fetch Production Run Data
    runs_query = db.query(database_models.ProductionRun).join(database_models.Product).filter(
        database_models.ProductionRun.machine_id.in_(machine_ids),
        database_models.ProductionRun.start_time <= end_time,
        database_models.ProductionRun.end_time >= start_time
    )
    runs_df = pd.read_sql(runs_query.statement, db.bind)
    if not runs_df.empty:
        products_df = pd.read_sql(db.query(database_models.Product).statement, db.bind)
        runs_df = pd.merge(runs_df, products_df[['id', 'product_name']], left_on='product_id', right_on='id', how='left')

    # 3. Fetch Maintenance Ticket Data
    tickets_query = db.query(database_models.MaintenanceTicket).filter(
        database_models.MaintenanceTicket.machine_id.in_(machine_ids),
        database_models.MaintenanceTicket.logged_time <= end_time
    )
    tickets_df = pd.read_sql(tickets_query.statement, db.bind)

    # 4. Perform the Temporal Join (Enrichment)
    fourjaw_df['product_name'] = None
    fourjaw_df['maintenance_ticket_id'] = None
    fourjaw_df['incident_category'] = None

    if not runs_df.empty:
        for _, run in runs_df.iterrows():
            mask = (
                (fourjaw_df['machine_id'] == run['machine_id']) &
                (fourjaw_df['start_timestamp'] >= run['start_time']) &
                (fourjaw_df['end_timestamp'] <= run['end_time'])
            )
            fourjaw_df.loc[mask, 'product_name'] = run['product_name']

    if not tickets_df.empty:
        # --- FIX #2: Ensure the index for the map is unique ---
        # First, drop any tickets that are not linked to a downtime event
        tickets_with_links = tickets_df.dropna(subset=['fourjaw_downtime_id'])
        # Then, drop any duplicates, keeping the first ticket linked to an event
        unique_tickets = tickets_with_links.drop_duplicates(subset=['fourjaw_downtime_id'], keep='first')
        
        if not unique_tickets.empty:
            ticket_map = unique_tickets.set_index('fourjaw_downtime_id')[['id', 'incident_category']].to_dict('index')
            
            fourjaw_df['maintenance_ticket_id'] = fourjaw_df['id'].map(lambda x: ticket_map.get(x, {}).get('id'))
            fourjaw_df['incident_category'] = fourjaw_df['id'].map(lambda x: ticket_map.get(x, {}).get('incident_category'))

    # 5. Return the enriched data as JSON
    return fourjaw_df.to_dict(orient="records")
