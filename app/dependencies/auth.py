
from fastapi import Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
from typing import Optional, List

from app.middlewares.authentication import AuthenticatedUser

bearer_scheme = HTTPBearer(auto_error=False)

def ensure_bearer(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    # Do nothing — this is just to make Swagger show the 🔒 button
    return

def get_authenticated_user():
    def dependency(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return user
    return dependency

def require_roles(required_roles: List[str]):
    def dependency(user: AuthenticatedUser = Depends(get_authenticated_user)):
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return dependency