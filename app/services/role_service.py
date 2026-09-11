"""Role Service - Role and permission management.

Quản lý vai trò (roles) và quyền hạn (permissions) trong hệ thống RBAC.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import (
    CodeRoleExistsException,
    PermissionDeniedException,
    PermissionNotFoundException,
    RoleNotFoundException,
)
from app.repositories.permission_repository import (
    PermissionRepoDep,
    PermissionRepository,
)
from app.repositories.role_repository import RoleRepoDep, RoleRepository
from app.schemas.role import PermissionResponse, RoleResponse


class RoleService:
    """Service quản lý vai trò và quyền hạn.
    
    Cung cấp các chức năng:
    - CRUD cho roles
    - Gán/gỡ permissions cho roles
    - Lấy danh sách permissions của role
    
    Attributes:
        role_repo: Repository để thao tác với Role entity.
        permission_repo: Repository để thao tác với Permission entity.
    """

    def __init__(self, 
        role_repo: RoleRepository,
        permission_repo: PermissionRepository
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo

    
    async def get_role(self, role_id: UUID) -> RoleResponse:
        """Lấy thông tin một role theo ID.
        
        Args:
            role_id: UUID của role cần lấy.
            
        Returns:
            RoleResponse chứa thông tin role.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
        """
        role = await self.role_repo.get_by_id(role_id)

        if not role: 
            raise RoleNotFoundException()
            
        return RoleResponse.model_validate(role)

    
    async def get_all_role(self) -> list[RoleResponse]:
        """Lấy danh sách tất cả roles.
        
        Returns:
            Danh sách RoleResponse.
        """
        result = await self.role_repo.get_all()
        return [RoleResponse.model_validate(row) for row in result]

    
    async def create_role(
        self, 
        code: str,
        name: str,
        description: str | None = None,
        is_default: bool = False,
        is_system: bool = False
    ) -> RoleResponse:
        """Tạo role mới.
        
        Args:
            code: Mã role (unique, ví dụ: 'admin', 'user').
            name: Tên hiển thị của role.
            description: Mô tả role (optional).
            is_default: Có phải role mặc định không.
            is_system: Có phải role hệ thống không.
            
        Returns:
            RoleResponse chứa thông tin role vừa tạo.
            
        Raises:
            CodeRoleExistsException: Mã role đã tồn tại.
        """
        code_existing = await self.role_repo.get_by_code(code)
        if code_existing: 
            raise CodeRoleExistsException()

        new_role = await self.role_repo.create(
            code=code,
            name=name,
            description=description,
            is_default=is_default,
            is_system=is_system
        )

        return RoleResponse.model_validate(new_role)
    

    async def update_role(
        self, 
        role_id: UUID, 
        code: str | None = None,
        name: str | None = None,
        description: str | None = None,
        is_default: bool | None = None,
        is_system: bool | None = None
    ) -> RoleResponse:
        """Cập nhật thông tin role.
        
        Chỉ cập nhật các field được truyền vào (không None).
        
        Args:
            role_id: UUID của role cần cập nhật.
            code: Mã role mới (optional).
            name: Tên mới (optional).
            description: Mô tả mới (optional).
            is_default: Trạng thái mặc định mới (optional).
            is_system: Trạng thái hệ thống mới (optional).
            
        Returns:
            RoleResponse chứa thông tin đã cập nhật.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
            CodeRoleExistsException: Mã role mới đã được sử dụng.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException()
        
        if code and code != role.code: 
            existing = await self.role_repo.get_by_code(code)
            if existing: 
                raise CodeRoleExistsException()
        
        update_data = {
            k: v for k, v in {
                "code": code,
                "name": name,
                "description": description,
                "is_default": is_default,
                "is_system": is_system
            }.items() if v is not None
        }
        
        updated_role = await self.role_repo.update(role, **update_data)

        return RoleResponse.model_validate(updated_role)


    async def delete_role(self, role_id: UUID) -> None:
        """Xóa một role.
        
        Không thể xóa system roles (is_system=True).
        
        Args:
            role_id: UUID của role cần xóa.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
            PermissionDeniedException: Không thể xóa system role.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role: 
            raise RoleNotFoundException()

        if role.is_system:
            raise PermissionDeniedException("Không thể xóa system roles")

        await self.role_repo.delete(role)
    

    async def assign_permission(self, role_id: UUID, permission_id: UUID) -> None:
        """Gán permission cho role.
        
        Args:
            role_id: UUID của role.
            permission_id: UUID của permission cần gán.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
            PermissionNotFoundException: Permission không tồn tại.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException()

        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise PermissionNotFoundException()
        
        await self.role_repo.add_permission(role_id, permission_id)


    async def remove_permission(self, role_id: UUID, permission_id: UUID) -> None:
        """Gỡ permission khỏi role.
        
        Args:
            role_id: UUID của role.
            permission_id: UUID của permission cần gỡ.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
            PermissionNotFoundException: Permission không tồn tại.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException()

        permission = await self.permission_repo.get_by_id(permission_id)
        if not permission:
            raise PermissionNotFoundException()
        
        await self.role_repo.remove_permission(role_id, permission_id)


    async def get_role_permissions(self, role_id: UUID) -> list[PermissionResponse]:
        """Lấy danh sách permissions của role.
        
        Args:
            role_id: UUID của role.
            
        Returns:
            Danh sách PermissionResponse.
            
        Raises:
            RoleNotFoundException: Role không tồn tại.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFoundException()
        
        result = await self.role_repo.get_role_permissions(role_id)

        return [PermissionResponse.model_validate(row) for row in result]


def get_role_service(
    role_repo: RoleRepoDep, 
    permission_repo: PermissionRepoDep
) -> RoleService:
    """Dependency injection factory cho RoleService."""
    return RoleService(role_repo, permission_repo)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]