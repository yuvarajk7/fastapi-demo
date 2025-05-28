import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class VersioningMiddleware(BaseHTTPMiddleware):
    version_regex = re.compile(r"^/v[0-9]+/")

    excluded_paths = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/swagger-ui.css",
        "/swagger-ui-bundle.js",
        "/static/",
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Check if path is in excluded paths
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return await call_next(request)

        if self.version_regex.match(path):
            return await call_next(request)

        version = "1"  # Default to v1

        # Rewrite path with appropriate version prefix
        request.scope["path"] = f"/v{version}" + path

        # Continue processing the request
        return await call_next(request)