from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import LoginInput, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Create access token",
    description="Create a JWT access token for authenticating to protected endpoints.",
    responses={
        status.HTTP_200_OK: {
            "description": "Access token successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
                        "token_type": "bearer",
                        "user": {
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "roles": ["admin", "user"]
                        }
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Incorrect email or password",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect email or password"
                    }
                }
            }
        }
    }
)
async def login_for_access_token(
        login_data: LoginInput,
        db: Session = Depends(get_db)
):
    """
    Login endpoint that returns a JWT token.

    - **email**: Email address of the user
    - **password**: User password

    Returns a JWT token and user info on success.
    """
    user = auth_service.authenticate_user(db, login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "roles": user["roles"]
        }
    }
