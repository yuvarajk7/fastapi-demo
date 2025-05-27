from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class InventoryItem(Base):
    """Database model for inventory items."""
    __tablename__ = "inventory_items"

    # Composite primary key
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), primary_key=True)
    
    # Additional fields
    quantity = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")
    
    def __repr__(self):
        return f"<InventoryItem(product_id={self.product_id}, location_id={self.location_id}, quantity={self.quantity})>"