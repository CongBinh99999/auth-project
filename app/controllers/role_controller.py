# app/controllers/role_controller.py
# 
# Purpose: Controller for Role management operations (RBAC).
# 
# Implementation details:
# - class RoleController:
#     def __init__(self, db: AsyncSession)
#     async def get_all_roles() -> list[RoleResponse]
#     async def get_role(role_id: UUID) -> RoleResponse
#     async def create_role(role_data: RoleCreate) -> RoleResponse
#     async def update_role(role_id: UUID, role_data: RoleUpdate) -> RoleResponse
#     async def delete_role(role_id: UUID) -> dict
#     async def get_role_permissions(role_id: UUID) -> list[PermissionResponse]
#     async def assign_permission(role_id: UUID, permission_id: UUID) -> dict
#     async def remove_permission(role_id: UUID, permission_id: UUID) -> dict
