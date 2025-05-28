from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.crud.inventory import inventory_repository
from app.crud.product import product_repository
from app.crud.location import location_repository
from app.dependencies.auth import get_current_user
from app.schemas.inventory import (
    InventoryUpdate, 
    InventoryItemResponse, 
    InventoryProductLocationResponse,
    InventoryLocationProductResponse
)
from app.core.responses import not_found

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(get_current_user(['admin', 'inventory_manager']))]
)


@router.get(
    "/by-product/{product_id}",
    response_model=List[InventoryProductLocationResponse],
    summary="Get inventory by product",
    description="Retrieve all inventory items for a specific product across all locations."
)
def get_inventory_by_product(
    product_id: int = Path(..., description="The unique ID of the product to retrieve inventory for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all inventory items for a specific product
    """
    # First check if product exists
    product = product_repository.get(db, product_id)
    if not product:
        not_found("Product", product_id)
        
    inventory_items = inventory_repository.get_by_product(db, product_id)
    result = []
    for inventory_item, location in inventory_items:
        result.append({
            "quantity": inventory_item.quantity,
            "reorder_point": inventory_item.reorder_point,
            "location_name": location.name,
            "location_id": location.id,
            "product_id": inventory_item.product_id,
            "in_stock": inventory_item.quantity > 0,
            "needs_reorder": inventory_item.quantity < inventory_item.reorder_point
        })
    return result


@router.get(
    "/by-location/{location_id}",
    response_model=List[InventoryLocationProductResponse],
    summary="Get inventory by location",
    description="Retrieve all inventory items at a specific location with product details."
)
def get_inventory_by_location(
    location_id: int = Path(..., description="The unique ID of the location to retrieve inventory for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all inventory items at a specific location
    """
    # First check if location exists
    location = location_repository.get(db, location_id)
    if not location:
        not_found("Location", location_id)
        
    inventory_items = inventory_repository.get_by_location(db, location_id)
    result = []
    for inventory_item, product in inventory_items:
        result.append({
            "quantity": inventory_item.quantity,
            "reorder_point": inventory_item.reorder_point,
            "product_name": product.name,
            "product_id": product.id,
            "location_id": inventory_item.location_id,
            "in_stock": inventory_item.quantity > 0,
            "needs_reorder": inventory_item.quantity < inventory_item.reorder_point
        })
    return result


@router.put(
    "/",
    response_model=InventoryItemResponse,
    summary="Update inventory stock",
    description="Update the stock quantity for a specific product at a specific location.",
    responses={
        status.HTTP_200_OK: {
            "description": "Stock updated successfully",
            "model": InventoryItemResponse
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Product or location not found",
            "content": {
                "application/json": {
                    "examples": {
                        "Product not found": {
                            "summary": "Product not found",
                            "value": {
                                "error": True,
                                "message": "Product with id 123 not found",
                                "details": {
                                    "record_type": "Product",
                                    "record_id": 123
                                }
                            }
                        },
                        "Location not found": {
                            "summary": "Location not found",
                            "value": {
                                "error": True,
                                "message": "Location with id 456 not found",
                                "details": {
                                    "record_type": "Location",
                                    "record_id": 456
                                }
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Insufficient stock",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Insufficient stock for product 123 and location 456",
                        "details": {
                            "product_id": 123,
                            "location_id": 456,
                            "requested": -10,
                            "available": 5
                        }
                    }
                }
            }
        }
    }
)
def update_inventory(update: InventoryUpdate, db: Session = Depends(get_db)):
    """
    Update inventory stock levels (add or remove stock)
    """
   
    result = inventory_repository.update_stock(
        db,
        product_id=update.product_id,
        location_id=update.location_id,
        quantity_change=update.quantity_change,
        reorder_point=update.reorder_point
    )
    return result