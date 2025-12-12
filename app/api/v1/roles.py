# app/api/v1/roles.py
# 
# Purpose: Role management endpoints (Admin only).
# 
# Implementation details:
# - router = APIRouter(prefix="/roles", tags=["Roles"])
# - GET / -> RoleController.get_all_roles (admin only)
# - GET /{role_id} -> RoleController.get_role
# - POST / -> RoleController.create_role (admin only)
# - PUT /{role_id} -> RoleController.update_role (admin only)
# - DELETE /{role_id} -> RoleController.delete_role (admin only)
# - GET /{role_id}/permissions -> RoleController.get_role_permissions
# - POST /{role_id}/permissions/{permission_id} -> assign permission
# - DELETE /{role_id}/permissions/{permission_id} -> remove permission
# - Dependencies: DbSession, ActiveUser, require_admin
