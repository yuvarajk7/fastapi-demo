from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Product(Base):
    """Database model for products."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(9), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"