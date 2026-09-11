from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.permission import Permission


class PermissionRepository: 
    """Repository cho Permission entity - quản lý các thao tác CRUD với bảng permissions."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 


    async def get_by_id(self, permission_id: UUID) -> Permission | None: 
        """Lấy permission theo ID.
        
        Args:
            permission_id: UUID của permission cần tìm.
            
        Returns:
            Permission nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(Permission)
            .where(Permission.id == permission_id)
        )

        return result.scalar_one_or_none()


    async def get_by_code(self, code: str) -> Permission | None: 
        """Lấy permission theo code.
        
        Args:
            code: Code của permission (VD: user:read, user:write).
            
        Returns:
            Permission nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(Permission)
            .where(Permission.code == code)
        )

        return result.scalar_one_or_none()


    async def get_by_module(self, module: str) -> list[Permission]: 
        """Lấy tất cả permissions của một module.
        
        Args:
            module: Tên module (VD: user, role, auth).
            
        Returns:
            Danh sách Permission objects thuộc module.
        """
        result = await self.db.execute(
            select(Permission)
            .where(Permission.module == module)
        )

        return list(result.scalars().all())


    async def get_all(self) -> list[Permission]: 
        """Lấy tất cả permissions trong hệ thống.
        
        Returns:
            Danh sách tất cả Permission objects.
        """
        result = await self.db.execute(
            select(Permission)
        )

        return list(result.scalars().all())


    async def create(self, **permission_data) -> Permission: 
        """Tạo permission mới.
        
        Args:
            **permission_data: Dữ liệu permission (name, code, module, ...).
            
        Returns:
            Permission đã được tạo.
        """
        permission = Permission(**permission_data) 
        
        self.db.add(permission)
        await self.db.flush()
        await self.db.refresh(permission)
        
        return permission


    async def delete(self, permission: Permission) -> None: 
        """Xóa permission khỏi database.
        
        Args:
            permission: Permission object cần xóa.
        """
        self.db.delete(permission)
        await self.db.flush()


def get_permission_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PermissionRepository: 
    """Dependency để inject PermissionRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        PermissionRepository instance.
    """
    return PermissionRepository(db)


PermissionRepoDep = Annotated[PermissionRepository, Depends(get_permission_repository)]