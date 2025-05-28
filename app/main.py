from fastapi import FastAPI, Depends

from app.middlewares.authentication import JWTAuthenticationMiddleware
from app.middlewares.version import VersioningMiddleware
from app.routers.v1 import v1_routers
from app.routers.v2 import v2_routers
from app.core.error_handlers import (inventory_exception_handler,sqlalchemy_exception_handler,general_exception_handler,
                                     user_exception_handler)
from app.core.exceptions import InventoryError, UserError
from sqlalchemy.exc import SQLAlchemyError
from app.middlewares.logging import LoggingMiddleware,RequestLogData
from app.core.logging import LoggerFactory
from app.dependencies.auth import ensure_bearer

# Create FastAPI app
app = FastAPI(
    title="Inventory Management API",
    description="API for managing inventory across multiple locations",
    version="1.0.0",
    dependencies=[Depends(ensure_bearer)]
)

console_logger = LoggerFactory.create_console_logger()
file_logger = LoggerFactory.create_file_logger(file_path="logs/api_requests.log")

def custom_log_handler(log_data: RequestLogData):
    log_message = (
        f"{log_data.method} {log_data.path} - "
        f"ID: {log_data.request_id} - "
        f"Status: {log_data.status_code} - "
        f"IP: {log_data.client_ip} - "
        f"UA: {log_data.user_agent} - "
        f"Duration: {log_data.duration_ms}ms"
    )
    console_logger.info(log_message)
    file_logger.info(log_message)

app.add_middleware(VersioningMiddleware)
app.add_middleware(LoggingMiddleware,log_handler=custom_log_handler)
app.add_middleware(JWTAuthenticationMiddleware)

app.add_exception_handler(InventoryError, inventory_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(UserError, user_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

for router in v1_routers:
    app.include_router(router,prefix="/v1")

for router in v2_routers:
    app.include_router(router,prefix="/v2")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify API is running"""
    return {
        "status": "online",
        "message": "Inventory Management API is running"
    }



# For development, we'll run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
