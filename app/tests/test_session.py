# app/tests/test_session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.core.security import get_password_hash
from app.crud import (
    product_repository,
    location_repository,
    inventory_repository,
    user_repository,
    role_repository,
)

# Hardcoded SQLite test DB (safe for local testing)
TEST_DATABASE_URL = "sqlite:///./inventory_test.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

def initialize_test_db():
    """Drop and recreate all tables, then insert known test data."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        # Create products
        product1 = product_repository.create(
            db, name="Laptop", description="16GB RAM", sku="LAP-10001", price=1299.99
        )
        product2 = product_repository.create(
            db, name="Smartphone", description="128GB Storage", sku="PHN-20002", price=799.99
        )
        product3 = product_repository.create(
            db, name="Tablet", description="Stylus support", sku="TAB-30003", price=499.99
        )

        # Create locations
        location1 = location_repository.create(
            db, name="Main Warehouse", address="123 Storage Ave", capacity=1000
        )
        location2 = location_repository.create(
            db, name="Downtown Store", address="456 Main St", capacity=200
        )
        location3 = location_repository.create(
            db, name="Mall Kiosk", address="789 Mall Blvd", capacity=50
        )

        # Inventory entries
        inventory_repository.update_stock(db, product1.id, location1.id, 50, 10)
        inventory_repository.update_stock(db, product1.id, location2.id, 10, 5)
        inventory_repository.update_stock(db, product2.id, location1.id, 100, 20)
        inventory_repository.update_stock(db, product2.id, location2.id, 25, 10)
        inventory_repository.update_stock(db, product2.id, location3.id, 15, 5)
        inventory_repository.update_stock(db, product3.id, location1.id, 75, 15)
        inventory_repository.update_stock(db, product3.id, location3.id, 8, 5)
        inventory_repository.update_stock(db, product3.id, location2.id, 2, 5)  # Low stock

        # Roles
        admin_role = role_repository.create(db, name="admin", description="Full access")
        manager_role = role_repository.create(db, name="inventory_manager", description="Inventory control")
        clerk_role = role_repository.create(db, name="sales_clerk", description="Sales access")

        # Users
        password = get_password_hash("password")
        admin_user = user_repository.create(db, "Super", "Admin", "admintest@globomantics.com", password)
        manager_user = user_repository.create(db, "Inventory", "managertest", "inventory@globomantics.com", password)
        clerk_user = user_repository.create(db, "Sales", "Clerk", "clerktest@globomantics.com", password)

        # Role assignments
        user_repository.update_roles(db, admin_user.id, [admin_role.id])
        user_repository.update_roles(db, manager_user.id, [manager_role.id])
        user_repository.update_roles(db, clerk_user.id, [clerk_role.id])

        db.commit()
        print("✅ Test database initialized with sample data.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing test database: {e}")
        raise
    finally:
        db.close()


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
