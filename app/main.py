from fastapi import FastAPI
from app.routers import routers
from app.core.error_handlers import inventory_exception_handler,sqlalchemy_exception_handler,general_exception_handler
from app.core.exceptions import InventoryError
from sqlalchemy.exc import SQLAlchemyError

# Create FastAPI app
app = FastAPI(
    title="Inventory Management API",
    description="API for managing inventory across multiple locations",
    version="1.0.0"
)
app.add_exception_handler(InventoryError, inventory_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

for router in routers:
    app.include_router(router)




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
