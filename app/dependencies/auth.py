
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
from typing import Optional, List
bearer_scheme = HTTPBearer(auto_error=False)

def ensure_bearer(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    # Do nothing — this is just to make Swagger show the 🔒 button
    return

def get_current_user(required_roles: Optional[List[str]] = None):
    def dependency(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        if required_roles:
            user_roles = getattr(user, "roles", [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this resource"
                )
    return dependency