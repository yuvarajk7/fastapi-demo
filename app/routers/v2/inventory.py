from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.crud.inventory import inventory_repository
from app.schemas.inventory import (
    InventoryItemResponse,
    InventoryUpdateV2,
    InventoryOperationType
)
from app.dependencies.auth import require_roles

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(require_roles(['admin','inventory_manager']))]
)


@router.put(
    "/",
    response_model=InventoryItemResponse,
    summary="Update inventory stock (V2)",
    description="Update inventory using an operation-based approach for more explicit and safer inventory management."
)
def update_inventory_v2(update: InventoryUpdateV2, db: Session = Depends(get_db)):
    """
    Update inventory stock levels using operation-based approach:
    - INCREMENT: Add stock
    - DECREMENT: Remove stock
    - SET: Set absolute stock level
    """

    # Map the operation-based request to the appropriate CRUD method
    if update.operation == InventoryOperationType.INCREMENT:
        # For increment, use the update_stock with positive quantity_change
        result = inventory_repository.update_stock(
            db,
            product_id=update.product_id,
            location_id=update.location_id,
            quantity_change=update.value,  # Positive for increment
            reorder_point=update.reorder_point
        )
    elif update.operation == InventoryOperationType.DECREMENT:
        # For decrement, use the update_stock with negative quantity_change
        result = inventory_repository.update_stock(
            db,
            product_id=update.product_id,
            location_id=update.location_id,
            quantity_change=-update.value,  # Negative for decrement
            reorder_point=update.reorder_point
        )
    elif update.operation == InventoryOperationType.SET:
        # For set, use the set_stock method
        result = inventory_repository.set_stock(
            db,
            product_id=update.product_id,
            location_id=update.location_id,
            quantity=update.value,  # Absolute value
            reorder_point=update.reorder_point
        )

    return result