# app/repositories/permission_repository.py
# 
# Purpose: Database access layer for Permission operations.
# 
# Implementation details:
# - class PermissionRepository:
#     def __init__(self, db: AsyncSession)
#     async def get_by_id(permission_id: UUID) -> Permission | None
#     async def get_by_code(code: str) -> Permission | None
#     async def get_by_module(module: str) -> list[Permission]
#     async def get_all() -> list[Permission]
#     async def create(permission_data) -> Permission
#     async def delete(permission: Permission) -> None
