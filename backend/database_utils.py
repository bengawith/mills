"""
Database utility functions for SQLite operations and health checks.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, SessionLocal, DATABASE_PATH

logger = logging.getLogger(__name__)

def check_database_health() -> bool:
    """
    Check if the database is accessible and healthy.
    Returns True if healthy, False otherwise.
    """
    try:
        with engine.connect() as connection:
            # Simple query to test connection
            result = connection.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def get_database_info() -> Dict[str, Any]:
    """
    Get information about the database.
    """
    try:
        db_path = Path(DATABASE_PATH)
        info = {
            "database_type": "SQLite",
            "database_path": str(db_path.absolute()),
            "database_exists": db_path.exists(),
            "database_size_mb": round(db_path.stat().st_size / (1024 * 1024), 2) if db_path.exists() else 0,
            "is_healthy": check_database_health()
        }
        
        if info["is_healthy"]:
            # Get table count
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ))
                info["table_count"] = result.scalar()
        
        return info
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {"error": str(e)}

def backup_database(backup_path: Optional[str] = None) -> str:
    """
    Create a backup of the SQLite database.
    """
    try:
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/mill_dash_backup_{timestamp}.db"
        
        # Ensure backup directory exists
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # SQLite backup using SQL command
        with engine.connect() as connection:
            connection.execute(text(f"VACUUM INTO '{backup_path}'"))
        
        logger.info(f"Database backed up successfully to {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        raise

def optimize_database() -> bool:
    """
    Optimize the SQLite database by running VACUUM and ANALYZE.
    """
    try:
        with engine.connect() as connection:
            # VACUUM reclaims unused space and defragments
            connection.execute(text("VACUUM"))
            # ANALYZE updates query optimization statistics
            connection.execute(text("ANALYZE"))
        
        logger.info("Database optimization completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")
        return False

def get_table_sizes() -> Dict[str, int]:
    """
    Get size information for all tables in the database.
    """
    try:
        sizes = {}
        with SessionLocal() as db:
            # Get all table names
            result = db.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ))
            tables = [row[0] for row in result]
            
            for table in tables:
                # Count rows in each table
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                sizes[table] = count_result.scalar()
        
        return sizes
    except Exception as e:
        logger.error(f"Failed to get table sizes: {str(e)}")
        return {}
