from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from app.core.security import decode_jwt_token


class AuthenticatedUser(BaseModel):
    id: str
    email: str
    roles: list[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request.state.user = None

        auth_header: Optional[str] = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()

            try:
                claims = decode_jwt_token(token)

                request.state.user = AuthenticatedUser(
                    id=claims["sub"],
                    email=claims["email"],
                    roles=claims.get("roles", []),
                    first_name=claims.get("first_name"),
                    last_name=claims.get("last_name"),
                )
                print(request.state.user)
            except ValueError:
                return JSONResponse(
                    {"detail": "Invalid or expired token"},
                    status_code=401
                )

        return await call_next(request)
