# app/api/router.py
# 
# Purpose: Main router aggregator.
# 
# Implementation details:
# - api_router = APIRouter(prefix="/api/v1")
# - Include auth_router from app.api.v1.auth
# - Include users_router from app.api.v1.users
# - Include roles_router from app.api.v1.roles
# - Include devices_router from app.api.v1.devices
