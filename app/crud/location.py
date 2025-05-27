from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.models.location import Location
from app.db.models.inventory import InventoryItem


class LocationRepository:
    def get(self, db: Session, location_id: int) -> Optional[Location]:
        """Get a location by ID"""
        return db.query(Location).filter(Location.id == location_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
        """Get all locations with pagination"""
        return db.query(Location).offset(skip).limit(limit).all()
    
    def search(self, db: Session, term: str, skip: int = 0, limit: int = 100) -> List[Location]:
        """Search locations by name or address"""
        return db.query(Location).filter(
            or_(
                Location.name.ilike(f"%{term}%"),
                Location.address.ilike(f"%{term}%")
            )
        ).offset(skip).limit(limit).all()
    
    def get_with_stock_count(self, db: Session, location_id: int) -> Optional[Tuple[Location, int]]:
        """
        Get a location with its current total stock count
        Returns tuple of (location, total_stock) or None if location not found
        """
        location = self.get(db, location_id)
        if not location:
            return None
        
        # Calculate total inventory at this location
        stock_count = db.query(func.coalesce(func.sum(InventoryItem.quantity), 0))\
            .filter(InventoryItem.location_id == location_id)\
            .scalar()
        
        return location, stock_count
    
    def get_all_with_stock_counts(self, db: Session, skip: int = 0, limit: int = 100) -> List[Tuple[Location, int]]:
        """
        Get all locations with their stock counts
        Returns list of tuples: [(location1, stock1), (location2, stock2), ...]
        """
        # First get all locations with pagination
        locations = self.get_all(db, skip=skip, limit=limit)
        
        # If no locations, return empty list
        if not locations:
            return []
            
        # Get location IDs for the query
        location_ids = [loc.id for loc in locations]
        
        # Query to get stock counts for all these locations in a single query
        stock_subquery = db.query(
            InventoryItem.location_id,
            func.coalesce(func.sum(InventoryItem.quantity), 0).label("total_stock")
        ).filter(
            InventoryItem.location_id.in_(location_ids)
        ).group_by(
            InventoryItem.location_id
        ).subquery()
        
        # Create a dictionary of location_id -> stock_count
        stock_counts = {}
        for row in db.query(stock_subquery).all():
            stock_counts[row.location_id] = row.total_stock
        
        # Create result list of tuples
        result = []
        for location in locations:
            # Get stock count from dictionary, default to 0 if not found
            stock = stock_counts.get(location.id, 0)
            result.append((location, stock))
            
        return result
    
    def create(self, db: Session, name: str, address: str, capacity: int) -> Location:
        """Create a new location"""
        location = Location(name=name, address=address, capacity=capacity)
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    def update(self, db: Session, location_id: int, 
               name: Optional[str] = None, 
               address: Optional[str] = None, 
               capacity: Optional[int] = None) -> Optional[Location]:
        """Update a location"""
        location = self.get(db, location_id)
        if not location:
            return None
        
        if name is not None:
            location.name = name
        if address is not None:
            location.address = address
        if capacity is not None:
            location.capacity = capacity
        
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    def delete(self, db: Session, location_id: int) -> bool:
        """Delete a location"""
        location = self.get(db, location_id)
        if not location:
            return False
        
        db.delete(location)
        db.commit()
        return True


# Create single instance for import
location_repository = LocationRepository()