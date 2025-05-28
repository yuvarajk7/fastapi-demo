from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.role import Role
from app.core.exceptions import UserError

class RoleRepository:
    def get(self, db: Session, role_id: int) -> Optional[Role]:
        """Get a role by ID"""
        return db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """Get a role by name"""
        return db.query(Role).filter(Role.name == name).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles with pagination"""
        return db.query(Role).offset(skip).limit(limit).all()

    def create(self, db: Session, name: str, description: Optional[str] = None) -> Role:
        """Create a new role"""
        # Check if role name already exists
        existing_role = self.get_by_name(db, name)
        if existing_role:
            raise UserError(
                message=f"Role with name {name} already exists",
                error_code="ROLE_DUPLICATE_NAME",
                details={"name": name}
            )

        role = Role(name=name, description=description)

        try:
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            raise UserError(
                message=f"Role with name {name} already exists",
                error_code="ROLE_DUPLICATE_NAME",
                details={"name": name}
            )

    def update(self, db: Session, role_id: int, name: Optional[str] = None,
               description: Optional[str] = None) -> Role:
        """Update a role's details"""
        role = self.get(db, role_id)
        if not role:
            raise UserError(
                message=f"Role with id {role_id} not found",
                error_code="ROLE_NOT_FOUND",
                details={"role_id": role_id}
            )

        if name is not None and name != role.name:
            # Check if new name already exists
            existing_role = self.get_by_name(db, name)
            if existing_role:
                raise UserError(
                    message=f"Role with name {name} already exists",
                    error_code="ROLE_DUPLICATE_NAME",
                    details={"name": name}
                )
            role.name = name

        if description is not None:
            role.description = description

        try:
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            raise UserError(
                message="Role update failed due to database constraint",
                error_code="ROLE_UPDATE_FAILED"
            )

    def delete(self, db: Session, role_id: int) -> bool:
        """Delete a role"""
        role = self.get(db, role_id)
        if not role:
            return False

        db.delete(role)
        db.commit()
        return True

# Create single instance for import
role_repository = RoleRepository()