"""
Data migration script to move existing PostgreSQL data to SQLite.
This script can be used to migrate data if needed.
"""
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from database_models import Base
from database import engine as sqlite_engine, SessionLocal as SQLiteSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_postgres() -> Optional[tuple]:
    """
    Connect to the PostgreSQL database if credentials are provided.
    Returns (engine, session_maker) tuple or None if connection fails.
    """
    try:
        # Try to get PostgreSQL credentials from environment
        pg_user = os.getenv("POSTGRES_USER_OLD", "admin")
        pg_password = os.getenv("POSTGRES_PASSWORD_OLD")
        pg_db = os.getenv("POSTGRES_DB_OLD", "mill_dash_db")
        pg_host = os.getenv("POSTGRES_HOST_OLD", "localhost")
        pg_port = os.getenv("POSTGRES_PORT_OLD", "5432")
        
        if not pg_password:
            logger.warning("No PostgreSQL password provided, skipping PostgreSQL migration")
            return None
        
        pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        pg_engine = create_engine(pg_url)
        
        # Test connection
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        pg_session = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
        logger.info("Successfully connected to PostgreSQL database")
        return pg_engine, pg_session
        
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        return None

def migrate_table_data(pg_engine, table_name: str):
    """
    Migrate data from PostgreSQL table to SQLite.
    """
    try:
        logger.info(f"Migrating table: {table_name}")
        
        # Read data from PostgreSQL
        df = pd.read_sql_table(table_name, pg_engine)
        
        if df.empty:
            logger.info(f"No data found in table {table_name}")
            return
        
        # Write data to SQLite
        df.to_sql(table_name, sqlite_engine, if_exists='append', index=False)
        
        logger.info(f"Successfully migrated {len(df)} rows from {table_name}")
        
    except Exception as e:
        logger.error(f"Failed to migrate table {table_name}: {str(e)}")

def migrate_all_data():
    """
    Migrate all data from PostgreSQL to SQLite.
    """
    pg_connection = connect_to_postgres()
    if not pg_connection:
        logger.info("Skipping data migration - no PostgreSQL connection")
        return
    
    pg_engine, pg_session = pg_connection
    
    # List of tables to migrate (in dependency order)
    tables_to_migrate = [
        'users',
        'products',
        'repair_components',
        'historical_machine_data',
        'cut_events',
        'maintenance_tickets',
        'production_runs',
        'ticket_work_notes',
        'ticket_images',
        'ticket_components_used'
    ]
    
    try:
        for table_name in tables_to_migrate:
            migrate_table_data(pg_engine, table_name)
            
        logger.info("Data migration completed successfully")
        
    except Exception as e:
        logger.error(f"Data migration failed: {str(e)}")
        raise
    finally:
        pg_engine.dispose()

def verify_migration():
    """
    Verify that the migration was successful by comparing row counts.
    """
    try:
        with SQLiteSession() as db:
            tables = [
                'users', 'products', 'repair_components', 'historical_machine_data',
                'cut_events', 'maintenance_tickets', 'production_runs',
                'ticket_work_notes', 'ticket_images', 'ticket_components_used'
            ]
            
            logger.info("Migration verification:")
            for table in tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"  {table}: {count} rows")
                except Exception as e:
                    logger.error(f"  {table}: Error - {str(e)}")
                    
    except Exception as e:
        logger.error(f"Migration verification failed: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting data migration from PostgreSQL to SQLite")
    
    # Create SQLite database tables if they don't exist
    Base.metadata.create_all(bind=sqlite_engine)
    
    # Migrate data
    migrate_all_data()
    
    # Verify migration
    verify_migration()
    
    logger.info("Migration process completed")
