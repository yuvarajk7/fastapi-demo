from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.product import Product


class ProductRepository:
    def get(self, db: Session, product_id: int) -> Optional[Product]:
        """Get a product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        """Get a product by SKU"""
        return db.query(Product).filter(Product.sku == sku).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return db.query(Product).offset(skip).limit(limit).all()
    
    def search(self, db: Session, term: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by term in name, description, or SKU"""
        return db.query(Product).filter(
            or_(
                Product.name.ilike(f"%{term}%"),
                Product.description.ilike(f"%{term}%"),
                Product.sku.ilike(f"%{term}%")
            )
        ).offset(skip).limit(limit).all()
    
    def filter_by_price(self, db: Session, min_price: Optional[float] = None, 
                        max_price: Optional[float] = None, skip: int = 0, 
                        limit: int = 100) -> List[Product]:
        """Filter products by price range"""
        query = db.query(Product)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, name: str, description: str, sku: str, price: float) -> Product:
        """Create a new product"""
        product = Product(name=name, description=description, sku=sku, price=price)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def update(self, db: Session, product_id: int, 
               name: Optional[str] = None, 
               description: Optional[str] = None, 
               sku: Optional[str] = None, 
               price: Optional[float] = None) -> Optional[Product]:
        """Update a product"""
        product = self.get(db, product_id)
        if not product:
            return None
        
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if sku is not None:
            product.sku = sku
        if price is not None:
            product.price = price
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    def delete(self, db: Session, product_id: int) -> bool:
        """Delete a product"""
        product = self.get(db, product_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True


# Create single instance for import
product_repository = ProductRepository()