# app/api/v1/users.py
# 
# Purpose: User management endpoints (Router layer).
# 
# Implementation details:
# - router = APIRouter(prefix="/users", tags=["Users"])
# - GET /me -> UserController.get_profile (requires auth)
# - PUT /me -> UserController.update_profile
# - PUT /change-password -> UserController.change_password
# - Dependencies: DbSession, ActiveUser
