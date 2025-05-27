from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.models.inventory import InventoryItem
from app.db.models.product import Product
from app.db.models.location import Location
from app.core.exceptions import RecordNotFoundError, InsufficientStockError

class InventoryRepository:
    def get(self, db: Session, product_id: int, location_id: int) -> Optional[InventoryItem]:
        """Get inventory item by product_id and location_id"""
        return db.query(InventoryItem).filter(
            and_(
                InventoryItem.product_id == product_id,
                InventoryItem.location_id == location_id
            )
        ).first()
    
    def get_by_product(self, db: Session, product_id: int) -> List[Tuple[InventoryItem, Location]]:
        """
        Get all inventory items for a specific product with location information
        Returns list of tuples: [(inventory_item1, location1), (inventory_item2, location2), ...]
        """
        return db.query(InventoryItem, Location)\
            .join(Location, InventoryItem.location_id == Location.id)\
            .filter(InventoryItem.product_id == product_id)\
            .all()
    
    def get_by_location(self, db: Session, location_id: int) -> List[Tuple[InventoryItem, Product]]:
        """
        Get all inventory items at a specific location with product information
        Returns list of tuples: [(inventory_item1, product1), (inventory_item2, product2), ...]
        """
        return db.query(InventoryItem, Product)\
            .join(Product, InventoryItem.product_id == Product.id)\
            .filter(InventoryItem.location_id == location_id)\
            .all()
    
    def get_low_stock_items(self, db: Session) -> List[Tuple[InventoryItem, Product, Location]]:
        """
        Get inventory items with quantity below reorder point
        Returns list of tuples: [(inventory_item1, product1, location1), ...]
        """
        return db.query(InventoryItem, Product, Location)\
            .join(Product, InventoryItem.product_id == Product.id)\
            .join(Location, InventoryItem.location_id == Location.id)\
            .filter(InventoryItem.quantity < InventoryItem.reorder_point)\
            .all()
    
    def get_total_quantity_by_product(self, db: Session, product_id: int) -> int:
        """Get total quantity of a product across all locations"""
        result = db.query(func.sum(InventoryItem.quantity))\
            .filter(InventoryItem.product_id == product_id)\
            .scalar()
        return result or 0
    
    def update_stock(self, db: Session, product_id: int, location_id: int, 
                    quantity_change: int, reorder_point: Optional[int] = None) -> Optional[InventoryItem]:
        """
        Update stock quantity by adding or removing (if negative) the specified amount
        Optionally update the reorder point
        Creates the inventory item if it doesn't exist and quantity_change is positive
        Returns None if:
          - Item doesn't exist and quantity_change is negative
          - Item exists but would have negative quantity after change
        """
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise RecordNotFoundError("Product", product_id)
        
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise RecordNotFoundError("Location", location_id)
        

        inventory_item = self.get(db, product_id, location_id)
        
        if not inventory_item:
            # Don't allow negative stock for non-existent items
            if quantity_change <= 0:
                raise InsufficientStockError(
                    product_id=product_id,
                    location_id=location_id,
                    requested=quantity_change,
                    available=0
                )
                
            # Create new inventory item
            inventory_item = InventoryItem(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity_change,
                reorder_point=reorder_point or 0
            )
        else:
            # Don't allow negative stock
            if inventory_item.quantity + quantity_change < 0:
                raise InsufficientStockError(
                    product_id=product_id,
                    location_id=location_id,
                    requested=quantity_change,
                    available=inventory_item.quantity
                )
                
            # Update existing inventory item
            inventory_item.quantity += quantity_change
            
            # Update reorder point if specified
            if reorder_point is not None:
                inventory_item.reorder_point = reorder_point
        
        db.add(inventory_item)
        db.commit()
        db.refresh(inventory_item)
        return inventory_item
    
    def set_stock(self, db: Session, product_id: int, location_id: int,
                 quantity: int, reorder_point: Optional[int] = None) -> Optional[InventoryItem]:
        """
        Set absolute stock quantity and optionally the reorder point
        Creates the inventory item if it doesn't exist
        """
        if quantity < 0:
            return None
            
        inventory_item = self.get(db, product_id, location_id)
        
        if not inventory_item:
            # Create new inventory item
            inventory_item = InventoryItem(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity,
                reorder_point=reorder_point or 0
            )
        else:
            # Update existing inventory item
            inventory_item.quantity = quantity
            
            # Update reorder point if specified
            if reorder_point is not None:
                inventory_item.reorder_point = reorder_point
        
        db.add(inventory_item)
        db.commit()
        db.refresh(inventory_item)
        return inventory_item
    
    def delete(self, db: Session, product_id: int, location_id: int) -> bool:
        """Delete an inventory item (used for administrative purposes only)"""
        inventory_item = self.get(db, product_id, location_id)
        if not inventory_item:
            return False
        
        db.delete(inventory_item)
        db.commit()
        return True


# Create single instance for import
inventory_repository = InventoryRepository()