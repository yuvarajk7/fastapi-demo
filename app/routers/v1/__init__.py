from app.routers.v1.products import router as products_router
from app.routers.v1.locations import router as locations_router
from app.routers.v1.inventory import router as inventory_router
from app.routers.v1.auth import router as  auth_router

v1_routers = [
    products_router,
    locations_router,
    inventory_router,
    auth_router
]
