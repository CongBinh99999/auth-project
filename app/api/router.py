from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.devices import router as device_router
from app.api.v1.roles import router as role_router
from app.api.v1.users import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(device_router)
api_router.include_router(role_router)
api_router.include_router(user_router)