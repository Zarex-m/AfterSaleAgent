from fastapi import APIRouter

from app.api.routes import health, auth, order, document,knowledge

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(order.router)
api_router.include_router(document.router)
api_router.include_router(knowledge.router)