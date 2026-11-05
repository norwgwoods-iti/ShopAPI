from fastapi import APIRouter
from shopapi.api.v1.endpoints.auth import router as auth_router
from shopapi.api.v1.endpoints.products import router as product_router
from shopapi.api.v1.endpoints.categories import router as category_router
from shopapi.api.v1.endpoints.cart import router as cart_router



main_router = APIRouter()
main_router.include_router(product_router)
main_router.include_router(category_router)
main_router.include_router(auth_router)
main_router.include_router(cart_router)