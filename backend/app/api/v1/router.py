from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    checklists,
    finance,
    guests,
    kua_documents,
    mahar_items,
    orders,
    plans,
    vendors,
    weddings,
)

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
api_router.include_router(
    vendors.router,
    prefix="/weddings/{wedding_id}/vendors",
    tags=["vendors"],
)
api_router.include_router(
    kua_documents.router,
    prefix="/weddings/{wedding_id}/kua-documents",
    tags=["kua-documents"],
)
api_router.include_router(
    mahar_items.router,
    prefix="/weddings/{wedding_id}/mahar-items",
    tags=["mahar-items"],
)
api_router.include_router(
    finance.router,
    prefix="/weddings/{wedding_id}",
    tags=["finance"],
)
