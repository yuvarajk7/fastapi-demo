from pydantic import BaseModel, Field

class LocationCreate(BaseModel):
    """Schema for creating a new location"""
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=5, max_length=200)
    capacity: int = Field(..., gt=0)


class LocationResponse(BaseModel):
    """Schema for location response"""
    id: int = Field(..., description="Unique location identifier")
    name: str = Field(..., description="Location name")
    address: str = Field(..., description="Location address")
    capacity: int = Field(..., description="Storage capacity")
    
    model_config = {
        "from_attributes": True,  
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Main Warehouse",
                "address": "123 Storage Ave, Warehouse District",
                "capacity": 5000
            }
        }
    }