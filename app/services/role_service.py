# app/services/role_service.py
# 
# Purpose: Role management business logic (RBAC).
# 
# Implementation details:
# - class RoleService:
#     def __init__(self, db: AsyncSession)
#     async def get_role(role_id: UUID) -> Role
#     async def get_role_by_code(code: str) -> Role
#     async def get_all_roles() -> list[Role]
#     async def create_role(role_data) -> Role
#     async def update_role(role_id: UUID, update_data) -> Role
#     async def delete_role(role_id: UUID) -> None
#     async def assign_permission(role_id: UUID, permission_id: UUID) -> None
#     async def remove_permission(role_id: UUID, permission_id: UUID) -> None
#     async def get_role_permissions(role_id: UUID) -> list[Permission]
