from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_jwt_token
from app.crud.users import user_repository

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by email and password
        """
        # Find the user by email
        user = user_repository.get_by_email(db, email)
        # Check if user exists and password is correct
        if not user or not verify_password(password, user.password):
            return None

        # Get user roles
        role_names = [role.name for role in user.roles]

        # Return user info
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": role_names
        }

    @staticmethod
    def create_access_token(user_data: Dict[str, Any]) -> str:
        """
        Create an access token for the user
        """
        # Create token payload
        payload = {
            "email": user_data["email"],
            "roles": user_data["roles"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"]
        }

        # Create JWT token with user ID as subject
        token = create_jwt_token(
            subject=user_data["id"],
            payload=payload
        )

        return token

# Create a single instance
auth_service = AuthService()