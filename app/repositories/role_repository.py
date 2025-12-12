# app/repositories/role_repository.py
# 
# Purpose: Database access layer for Role operations.
# 
# Implementation details:
# - class RoleRepository:
#     def __init__(self, db: AsyncSession)
#     async def get_by_id(role_id: UUID) -> Role | None
#     async def get_by_code(code: str) -> Role | None
#     async def get_default_role() -> Role | None
#     async def get_all() -> list[Role]
#     async def create(role_data) -> Role
#     async def update(role: Role, update_data) -> Role
#     async def delete(role: Role) -> None
#     async def get_role_permissions(role_id: UUID) -> list[Permission]
