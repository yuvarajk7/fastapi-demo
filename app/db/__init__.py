from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.db.models import product, location, inventory
def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Create tables
    Base.metadata.create_all(bind=engine)