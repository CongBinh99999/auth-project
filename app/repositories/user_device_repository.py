from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.user_device import UserDevice


class UserDeviceRepository: 
    """Repository cho UserDevice entity - quản lý các thao tác CRUD với bảng user_devices."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 

    
    async def get_by_id(self, device_id: UUID) -> UserDevice | None: 
        """Lấy device theo ID.
        
        Args:
            device_id: UUID của device cần tìm.
            
        Returns:
            UserDevice nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(UserDevice)
            .where(UserDevice.id == device_id)
        )

        return result.scalar_one_or_none()


    async def get_by_user_id(self, user_id: UUID) -> list[UserDevice]: 
        """Lấy tất cả devices của một user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Danh sách UserDevice objects của user.
        """
        result = await self.db.execute(
            select(UserDevice)
            .where(UserDevice.user_id == user_id)
        )

        return list(result.scalars().all())


    async def get_by_fingerprint(self, user_id: UUID, fingerprint: str) -> UserDevice | None: 
        """Lấy device theo fingerprint của user.
        
        Args:
            user_id: UUID của user.
            fingerprint: Device fingerprint.
            
        Returns:
            UserDevice nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(UserDevice)
            .where(
                and_(
                    UserDevice.user_id == user_id, 
                    UserDevice.fingerprint == fingerprint
                )
            )
            .order_by(UserDevice.created_at)
        )

        # first() chứ không phải scalar_one_or_none(): không có ràng buộc unique
        # trên (user_id, fingerprint), nên hai login đồng thời có thể cùng tạo
        # một dòng. scalar_one_or_none() sẽ ném MultipleResultsFound và khoá
        # user ra khỏi hệ thống bằng lỗi 500 ở mọi lần đăng nhập sau đó.
        return result.scalars().first()

        
    async def create(self, **device_data) -> UserDevice: 
        """Tạo device mới.
        
        Args:
            **device_data: Dữ liệu device (user_id, fingerprint, device_name, ...).
            
        Returns:
            UserDevice đã được tạo.
        """
        device = UserDevice(**device_data)

        self.db.add(device)
        await self.db.flush()
        await self.db.refresh(device)

        return device 


    async def update(self, device: UserDevice, **update_data) -> UserDevice:
        """Cập nhật thông tin device.
        
        Args:
            device: UserDevice object cần cập nhật.
            **update_data: Dữ liệu cần cập nhật.
            
        Returns:
            UserDevice đã được cập nhật.
        """
        for key, value in update_data.items(): 
            if hasattr(device, key): 
                setattr(device, key, value)

        device.updated_at = datetime.now(UTC)

        await self.db.flush()
        await self.db.refresh(device)

        return device


    async def update_last_login(self, device: UserDevice) -> UserDevice:
        """Cập nhật thời gian đăng nhập gần nhất của device.
        
        Args:
            device: UserDevice object cần cập nhật.
            
        Returns:
            UserDevice đã được cập nhật.
        """
        device.last_login_at = datetime.now(UTC)

        await self.db.flush()
        await self.db.refresh(device)

        return device


    async def set_status(self, device: UserDevice, status: str) -> UserDevice: 
        """Cập nhật trạng thái device.
        
        Args:
            device: UserDevice object cần cập nhật.
            status: Trạng thái mới (active, inactive, blocked).
            
        Returns:
            UserDevice đã được cập nhật.
        """
        device.status = status

        await self.db.flush()
        await self.db.refresh(device)

        return device


    async def set_trusted(self, device: UserDevice, is_trusted: bool) -> UserDevice: 
        """Đánh dấu device là trusted hoặc untrusted.
        
        Args:
            device: UserDevice object cần cập nhật.
            is_trusted: True nếu trusted, False nếu không.
            
        Returns:
            UserDevice đã được cập nhật.
        """
        device.is_trusted = is_trusted

        await self.db.flush()
        await self.db.refresh(device)

        return device


    async def delete(self, device: UserDevice) -> None: 
        """Xóa device khỏi database.
        
        Args:
            device: UserDevice object cần xóa.
        """
        self.db.delete(device)
        await self.db.flush()


    async def delete_all_by_user(self, user_id: UUID) -> int: 
        """Xóa tất cả devices của một user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng devices đã xóa.
        """
        result = await self.db.execute(
            delete(UserDevice)
            .where(UserDevice.user_id == user_id)
        )

        await self.db.flush()

        return result.rowcount
    

    async def get_device_by_id(self, device_id: UUID, user_id: UUID) -> UserDevice | None: 
        result = await self.db.execute(
            select(UserDevice)
            .where(
                and_(
                    UserDevice.id == device_id, 
                    UserDevice.user_id == user_id
                )
            )
        )
        
        return result.scalar_one_or_none()


def get_user_device_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserDeviceRepository:
    """Dependency để inject UserDeviceRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        UserDeviceRepository instance.
    """
    return UserDeviceRepository(db)


UserDeviceRepoDep = Annotated[UserDeviceRepository, Depends(get_user_device_repository)]