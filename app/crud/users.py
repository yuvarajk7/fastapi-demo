from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.db.models.user import User
from app.db.models.role import Role
from app.core.exceptions import UserError

class UserRepository:
    def get(self, db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID with roles loaded"""
        return db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email with roles loaded"""
        return db.query(User).options(joinedload(User.roles)).filter(User.email == email).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination and roles loaded"""
        return db.query(User).options(joinedload(User.roles)).offset(skip).limit(limit).all()

    def create(self, db: Session, first_name: str, last_name: str, email: str, password: str) -> User:
        """Create a new user"""
        # Check if email already exists
        existing_user = self.get_by_email(db, email)
        if existing_user:
            raise UserError(
                message=f"User with email {email} already exists",
                error_code="USER_DUPLICATE_EMAIL",
                details={"email": email}
            )

        user = User(first_name=first_name, last_name=last_name, email=email, password=password)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            # This handles race conditions where the email might be added between our check and insert
            raise UserError(
                message=f"User with email {email} already exists",
                error_code="USER_DUPLICATE_EMAIL",
                details={"email": email}
            )

    def update_roles(self, db: Session, user_id: int, role_ids: List[int]) -> User:
        """
        Update user roles (replaces all existing roles with the new set)
        """
        user = self.get(db, user_id)
        if not user:
            raise UserError(
                message=f"User with id {user_id} not found",
                error_code="USER_NOT_FOUND",
                details={"user_id": user_id}
            )

        # Clear existing roles
        user.roles = []

        # Fetch and assign new roles
        for role_id in role_ids:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise UserError(
                    message=f"Role with id {role_id} not found",
                    error_code="ROLE_NOT_FOUND",
                    details={"role_id": role_id}
                )
            user.roles.append(role)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # Optional: Update user details method
    # def update(self, db: Session, user_id: int,
    #            first_name: Optional[str] = None,
    #            last_name: Optional[str] = None,
    #            email: Optional[str] = None) -> Optional[User]:
    #     """Update user details"""
    #     # Implementation would go here

    def delete(self, db: Session, user_id: int) -> bool:
        """Delete a user"""
        user = self.get(db, user_id)
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True

# Create single instance for import
user_repository = UserRepository()