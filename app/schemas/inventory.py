# app/schemas/inventory.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional

class InventoryItemResponse(BaseModel):
    product_id: int = Field(..., description="ID of the product")
    location_id: int = Field(..., description="ID of the storage location")
    quantity: int = Field(..., description="Current quantity in stock")
    reorder_point: int = Field(..., description="Quantity at which to reorder")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "product_id": 1,
                "location_id": 5,
                "quantity": 42,
                "reorder_point": 10
            }
        }
    }
class InventoryUpdate(BaseModel):
    """Schema for updating inventory stock levels"""
    product_id: int = Field(..., gt=0)
    location_id: int = Field(..., gt=0)
    quantity_change: int   
    reorder_point: Optional[int] = Field(None, ge=0)
    reason: Optional[str] = None   

    @field_validator('quantity_change') 
    def validate_quantity_change(cls, v):
        """Validate quantity change is reasonable"""
        # Limit single transaction size to prevent errors
        if abs(v) > 100000:
            raise ValueError('Quantity change cannot exceed 1000 units in a single operation')
        return v
 
    @model_validator(mode='after')
    def validate_inventory_operations(self):
        """Validate business rules across multiple fields"""
        # For significant stock reductions, require a reason
        if self.quantity_change and self.quantity_change < -50 and not self.reason:
            raise ValueError('Stock reductions of more than 50 units require a reason')

        # For extremely large changes in either direction, require detailed reason
        if self.quantity_change and abs(self.quantity_change) > 200 and (not self.reason or len(self.reason) < 20):
            raise ValueError('Changes of more than 200 units require a detailed reason (at least 20 characters)')

        return self
    
class InventoryProductLocationResponse(BaseModel):
    """Schema for inventory items by product and location"""
    quantity: int = Field(..., description="Current quantity in stock")
    reorder_point: int = Field(..., description="Quantity at which to reorder")
    location_name: str = Field(..., description="Name of the storage location")
    location_id: int = Field(..., description="ID of the storage location")
    product_id: int = Field(..., description="ID of the product")
    in_stock: bool = Field(..., description="Whether the item is in stock")
    needs_reorder: bool = Field(..., description="Whether the stock is below reorder point")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "quantity": 42,
                "reorder_point": 10,
                "location_name": "Main Warehouse",
                "location_id": 1,
                "product_id": 5,
                "in_stock": True,
                "needs_reorder": False
            }
        }
    }

class InventoryLocationProductResponse(BaseModel):
    """Schema for inventory items by location and product"""
    quantity: int = Field(..., description="Current quantity in stock")
    reorder_point: int = Field(..., description="Quantity at which to reorder")
    product_name: str = Field(..., description="Name of the product")
    product_id: int = Field(..., description="ID of the product")
    location_id: int = Field(..., description="ID of the storage location")
    in_stock: bool = Field(..., description="Whether the item is in stock")
    needs_reorder: bool = Field(..., description="Whether the stock is below reorder point")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "quantity": 42,
                "reorder_point": 10,
                "product_name": "Wireless Keyboard",
                "product_id": 5,
                "location_id": 1,
                "in_stock": True,
                "needs_reorder": False
            }
        }
    }
