
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

def ensure_bearer(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    # Do nothing — this is just to make Swagger show the 🔒 button
    return