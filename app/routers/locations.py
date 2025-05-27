from fastapi import APIRouter, Depends,Path,Query,status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.location import location_repository
from app.schemas.location import LocationCreate,LocationResponse
from app.core.responses import not_found
from typing import List, Optional


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

@router.get(
    "/",
    response_model=List[LocationResponse],
    summary="List all locations",
    description="Retrieve a paginated list of locations with optional search filtering."
)
def list_locations(
    search: Optional[str] = Query(None, description="Search term for filtering locations by name or address"),
    skip: int = Query(0, ge=0, description="Number of rows to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve locations with optional search and pagination
    """
    if search:
        return location_repository.search(db, search, skip=skip, limit=limit)
    else:
        return location_repository.get_all(db, skip=skip, limit=limit)


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get location by ID",
    description="Retrieve detailed information about a specific location by its ID.",
    responses={
        status.HTTP_200_OK: {
            "description": "Location found successfully",
            "model": LocationResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Location not found",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Location not found",
                        "details": {
                            "resource_type": "Location",
                            "resource_id": "123"
                        }
                    }
                }
            }
        }
    }
)
def get_location(
    location_id: int = Path(..., description="The unique ID of the location to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a Location by ID
    """
    location = location_repository.get(db, location_id)
    if not location:
        not_found("Location", location_id)
    return location


@router.post(
    "/",
    response_model=LocationResponse,
    summary="Create new location",
    description="Create a new warehouse or storage location in the system."
)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new location
    """
    return location_repository.create(
        db, 
        name=location.name,
        address=location.address,
        capacity=location.capacity
    )