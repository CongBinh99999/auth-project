from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission


class RoleRepository: 
    """Repository cho Role entity - quản lý các thao tác CRUD với bảng roles."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db


    async def get_by_id(self, role_id: UUID) -> Role | None: 
        """Lấy role theo ID.
        
        Args:
            role_id: UUID của role cần tìm.
            
        Returns:
            Role nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.id == role_id)
        )

        return result.scalar_one_or_none()
    

    async def get_by_code(self, code: str) -> Role | None: 
        """Lấy role theo code.
        
        Args:
            code: Code của role (VD: ADMIN, USER).
            
        Returns:
            Role nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.code == code)
        )

        return result.scalar_one_or_none()


    async def get_default_role(self) -> Role | None:
        """Lấy role mặc định của hệ thống.
        
        Returns:
            Role có is_default=True, None nếu không có.
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.is_default == True)
        )

        return result.scalar_one_or_none()

    
    async def get_all(self) -> list[Role]: 
        """Lấy tất cả roles trong hệ thống.
        
        Returns:
            Danh sách tất cả Role objects.
        """
        result = await self.db.execute(
            select(Role)
        )

        return list(result.scalars().all())
    
    
    async def create(self, **role_data) -> Role: 
        """Tạo role mới.
        
        Args:
            **role_data: Dữ liệu role (name, code, description, ...).
            
        Returns:
            Role đã được tạo.
        """
        role = Role(**role_data)

        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)

        return role 
    

    async def update(self, role: Role, **update_data) -> Role: 
        """Cập nhật thông tin role.
        
        Args:
            role: Role object cần cập nhật.
            **update_data: Dữ liệu cần cập nhật.
            
        Returns:
            Role đã được cập nhật.
        """
        for key, value in update_data.items(): 
            if hasattr(role, key): 
                setattr(role, key, value)

        role.updated_at = datetime.now(UTC)

        await self.db.flush()
        await self.db.refresh(role)

        return role

    
    async def delete(self, role: Role) -> None: 
        """Xóa role khỏi database.
        
        Args:
            role: Role object cần xóa.
        """
        self.db.delete(role)
        await self.db.flush()


    async def get_role_permissions(self, role_id: UUID) -> list[Permission]:
        """Lấy danh sách permissions của một role.
        
        Args:
            role_id: UUID của role.
            
        Returns:
            Danh sách Permission objects thuộc role.
        """
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == role_id)
        )
        
        return list(result.scalars().all())

    
    async def add_permission(self, role_id: UUID, permission_id: UUID) -> None: 
        result = await self.db.execute(
            select(RolePermission)
            .filter_by(
                role_id = role_id, 
                permission_id = permission_id
            )
        )
        existing = result.scalars().first()

        if not existing: 
            new_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(new_permission) 
            await self.db.flush()


    async def remove_permission(self, role_id: UUID, permission_id: UUID) -> None: 
        await self.db.execute(
            delete(RolePermission)
            .where(
                RolePermission.role_id == role_id, 
                RolePermission.permission_id == permission_id
            )
        )
        await self.db.flush()


def get_role_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> RoleRepository: 
    """Dependency để inject RoleRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        RoleRepository instance.
    """
    return RoleRepository(db)


RoleRepoDep = Annotated[RoleRepository, Depends(get_role_repository)]