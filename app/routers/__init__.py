from app.routers.products import router as products_router
from app.routers.locations import router as locations_router
from app.routers.inventory import router as inventory_router
routers = [
    products_router,
    locations_router,
    inventory_router
]
