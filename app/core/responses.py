from fastapi import HTTPException, status
from typing import Any, Dict, Optional

def not_found(resource_type: str, resource_id: Any, details: Optional[Dict] = None):
    """Helper function to raise a standardized 404 Not Found exception"""
    error_details = details or {}
    error_details.update({
        "resource_type": resource_type,
        "resource_id": resource_id
    })
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": f"{resource_type} not found",
            "details": error_details
        }
    )