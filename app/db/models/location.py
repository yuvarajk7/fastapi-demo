from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Location(Base):
    """Database model for storage locations."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=False)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="location", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"