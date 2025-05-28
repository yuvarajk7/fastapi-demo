from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext

from app.core.config import JWT

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(
        subject: Union[str, int],
        payload: Dict[str, Any] = {},
        expires_minutes: Optional[int] = None
) -> str:
    """
    Create a JWT token
    """
    expires_delta = expires_minutes or JWT.EXPIRATION_MINUTES
    now = datetime.now(timezone.utc)
    to_encode = payload.copy()
    expire = now + timedelta(minutes=expires_delta)

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "sub": str(subject),
        "iat": now,
        "iss": JWT.ISSUER
    })

    # Create the JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        JWT.SECRET_KEY,
        algorithm=JWT.ALGORITHM
    )

    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token
    """
    try:
        payload = jwt.decode(
            token,
            JWT.SECRET_KEY,
            algorithms=[JWT.ALGORITHM],
            issuer=JWT.ISSUER
        )
        return payload
    except jwt.PyJWTError:
        raise ValueError("Invalid token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)