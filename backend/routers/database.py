"""
Database management router for SQLite operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any
import logging

from security import get_current_active_user
from database_utils import (
    check_database_health,
    get_database_info, 
    backup_database,
    optimize_database,
    get_table_sizes
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/database",
    tags=["Database Management"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/health", response_model=Dict[str, bool])
async def database_health():
    """Check database health status."""
    try:
        is_healthy = check_database_health()
        return {"healthy": is_healthy}
    except Exception as e:
        logger.error(f"Failed to check database health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check database health")

@router.get("/info", response_model=Dict[str, Any])
async def database_info():
    """Get detailed database information."""
    try:
        info = get_database_info()
        if "error" in info:
            raise HTTPException(status_code=500, detail=info["error"])
        return info
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get database information")

@router.get("/tables", response_model=Dict[str, int])
async def table_sizes():
    """Get row counts for all tables."""
    try:
        sizes = get_table_sizes()
        return sizes
    except Exception as e:
        logger.error(f"Failed to get table sizes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get table information")

@router.post("/backup")
async def create_backup():
    """Create a database backup."""
    try:
        backup_path = backup_database()
        return {"message": "Backup created successfully", "backup_path": backup_path}
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create database backup")

@router.post("/optimize")
async def optimize():
    """Optimize the database (VACUUM and ANALYZE)."""
    try:
        success = optimize_database()
        if success:
            return {"message": "Database optimization completed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Database optimization failed")
    except Exception as e:
        logger.error(f"Failed to optimize database: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize database")

@router.get("/download-backup")
async def download_latest_backup():
    """Download the latest database backup file."""
    try:
        # Create a fresh backup for download
        backup_path = backup_database()
        return FileResponse(
            path=backup_path,
            filename="mill_dash_backup.db",
            media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Failed to create backup for download: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create backup for download")
