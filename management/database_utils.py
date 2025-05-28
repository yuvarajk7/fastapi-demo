import sys
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from app.core.security import get_password_hash

# Import from app
from app.db.session import engine, SessionLocal, Base
from app.db import init_db
from app.crud import product_repository, location_repository, inventory_repository, user_repository,role_repository


def check_database_exists():
    """Check if the database has been initialized with tables"""
    try:
        with engine.connect() as conn:
            inspector = sa.inspect(engine)
            has_tables = inspector.get_table_names()
            return len(has_tables) > 0
    except SQLAlchemyError:
        return False


def init_database(force_recreate=False):
    """Initialize the database tables, dropping existing tables if requested"""
    db_exists = check_database_exists()
    
    if db_exists:
        if force_recreate:
            print("Dropping all existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("Tables dropped successfully.")
        else:
            print("Database already exists.")
            return False
    
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully.")
    return True


def create_sample_data(force_recreate=False):
    """Create sample data for testing"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_products = product_repository.get_all(db)
        if existing_products and not force_recreate:
            print(f"Database already contains {len(existing_products)} products.")
            return False
        
        if existing_products and force_recreate:
            print("Clearing existing data...")
            # Delete all existing data (relies on cascade delete in your models)
            for product in existing_products:
                product_repository.delete(db, product.id)
            print("Existing data cleared.")
        
        # Create sample products
        print("Creating sample products...")
        product1 = product_repository.create(
            db=db,
            name="Laptop",
            description="High-performance laptop with 16GB RAM",
            sku="LAP-10001",
            price=1299.99
        )
        
        product2 = product_repository.create(
            db=db,
            name="Smartphone",
            description="Latest model with 128GB storage",
            sku="PHN-20002",
            price=799.99
        )
        
        product3 = product_repository.create(
            db=db,
            name="Tablet",
            description="10-inch tablet with stylus support",
            sku="TAB-30003",
            price=499.99
        )
        
        # Create sample locations
        print("Creating sample locations...")
        location1 = location_repository.create(
            db=db,
            name="Main Warehouse",
            address="123 Storage Ave, Warehouse District",
            capacity=1000
        )
        
        location2 = location_repository.create(
            db=db,
            name="Downtown Store",
            address="456 Main St, Downtown",
            capacity=200
        )
        
        location3 = location_repository.create(
            db=db,
            name="Mall Kiosk",
            address="789 Shopping Center Blvd, Mall",
            capacity=50
        )
        
        # Create inventory items
        print("Creating inventory records...")
        inventory_repository.update_stock(
            db=db,
            product_id=product1.id,
            location_id=location1.id,
            quantity_change=50,
            reorder_point=10
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product1.id,
            location_id=location2.id,
            quantity_change=10,
            reorder_point=5
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product2.id,
            location_id=location1.id,
            quantity_change=100,
            reorder_point=20
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product2.id,
            location_id=location2.id,
            quantity_change=25,
            reorder_point=10
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product2.id,
            location_id=location3.id,
            quantity_change=15,
            reorder_point=5
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product3.id,
            location_id=location1.id,
            quantity_change=75,
            reorder_point=15
        )
        
        inventory_repository.update_stock(
            db=db,
            product_id=product3.id,
            location_id=location3.id,
            quantity_change=8,
            reorder_point=5
        )
        
        # Create a low stock situation for testing
        inventory_repository.update_stock(
            db=db,
            product_id=product3.id,
            location_id=location2.id,
            quantity_change=2,
            reorder_point=5
        )

        # Create sample roles
        print("Creating user roles...")
        admin_role = role_repository.create(
            db=db,
            name="admin",
            description="Administrator with full access to all features"
        )

        inventory_manager_role = role_repository.create(
            db=db,
            name="inventory_manager",
            description="Can manage inventory levels and locations"
        )

        sales_clerk_role = role_repository.create(
            db=db,
            name="sales_clerk",
            description="Can view inventory and process sales"
        )

        password_hash = get_password_hash("password")

        # Create sample users
        print("Creating sample users...")
        admin_user = user_repository.create(
            db=db,
            first_name="Super",
            last_name="Admin",
            email="admin@globomantics.com",
            password=password_hash
        )

        manager_user = user_repository.create(
            db=db,
            first_name="Inventory",
            last_name="Manager",
            email="inventory@globomantics.com",
            password=password_hash
        )

        clerk_user = user_repository.create(
            db=db,
            first_name="Sales",
            last_name="Clerk",
            email="clerk@globomantics.com",
            password=password_hash
        )

        # Assign roles to users
        print("Assigning roles to users...")
        user_repository.update_roles(db, admin_user.id, [admin_role.id])
        user_repository.update_roles(db, manager_user.id, [inventory_manager_role.id])
        user_repository.update_roles(db, clerk_user.id, [sales_clerk_role.id])

        print("Sample data created successfully.")
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()