from fastapi import APIRouter

from app.api.v1 import admin, auth, checklists, guests, orders, plans, weddings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(admin.router, prefix="/admin/orders", tags=["admin"])
api_router.include_router(weddings.router, prefix="/weddings", tags=["weddings"])
api_router.include_router(
    orders.router,
    prefix="/weddings/{wedding_id}/orders",
    tags=["orders"],
)
api_router.include_router(
    guests.router,
    prefix="/weddings/{wedding_id}/guests",
    tags=["guests"],
)
api_router.include_router(
    checklists.router,
    prefix="/weddings/{wedding_id}/checklists",
    tags=["checklists"],
)
