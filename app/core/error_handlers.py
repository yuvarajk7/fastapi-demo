from fastapi import Request,status
from fastapi.responses import JSONResponse

from app.core.exceptions import InventoryError
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import UserError

async def user_exception_handler(request: Request, exc: UserError):
    """Handler for user-related exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )

async def inventory_exception_handler(request: Request, exc: InventoryError):
    """Handler for our custom inventory exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemy database errors"""
    # Log the full exception details for debugging
    print(f"Database error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "A database error occurred",
            "details": {
                "error_type": exc.__class__.__name__,
                # Provide a simplified message for the client
                "error": "The operation couldn't be completed due to a database error"
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handler for any unhandled exceptions"""
    # Log the full exception details for debugging
    print(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "details": {
                "error_type": exc.__class__.__name__
                # Don't expose internal error details to clients
            }
        }
    )