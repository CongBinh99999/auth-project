"""Device Service - User device management.

Quản lý các thiết bị đăng nhập của user bao gồm đăng ký,
trust/untrust, block và xóa devices.
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import DeviceBlockedException, DeviceNotFoundException
from app.models.user_device import UserDevice
from app.repositories.token_family_repository import (
    TokenFamilyRepoDep,
    TokenFamilyRepository,
)
from app.repositories.user_device_repository import (
    UserDeviceRepoDep,
    UserDeviceRepository,
)
from app.schemas.device import DeviceUpdate
from app.utils.constants import DeviceStatus


class DeviceService:
    """Service quản lý thiết bị đăng nhập của user.
    
    Cung cấp các chức năng:
    - Đăng ký device mới hoặc cập nhật device đã có
    - Trust/Untrust devices
    - Block/Remove devices
    - Lấy danh sách devices của user
    
    Attributes:
        device_repo: Repository để thao tác với UserDevice entity.
    """

    def __init__(
        self,
        device_repo: UserDeviceRepository,
        family_repo: TokenFamilyRepository | None = None,
    ):
        self.device_repo = device_repo
        self.family_repo = family_repo


    async def register_device(
        self, 
        user_id: UUID,
        fingerprint: str | None = None,
        device_name: str | None = None,
        device_type: str | None = None,
        browser: str | None = None,
        os: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> UserDevice:
        """Đăng ký device mới hoặc cập nhật device đã có.
        
        Nếu device với fingerprint đã tồn tại → cập nhật thông tin.
        Nếu chưa → tạo mới.
        
        Args:
            user_id: UUID của user.
            fingerprint: Device fingerprint để nhận diện device.
            device_name: Tên thiết bị (ví dụ: "iPhone của Minh").
            device_type: Loại thiết bị (mobile, desktop, tablet).
            browser: Tên trình duyệt.
            os: Hệ điều hành.
            ip_address: IP address.
            user_agent: User agent string.
            
        Returns:
            UserDevice entity (mới tạo hoặc đã cập nhật).
        """
        device = None 

        if fingerprint: 
            device = await self.device_repo.get_by_fingerprint(user_id, fingerprint)
        
        if device and device.status == DeviceStatus.BLOCKED:
            raise DeviceBlockedException()

        if not device: 
            return await self.device_repo.create(
                user_id=user_id,
                fingerprint=fingerprint,
                device_name=device_name,
                device_type=device_type,
                browser=browser,
                os=os,
                ip_address=ip_address,
                user_agent=user_agent,
                last_login_at=datetime.now(UTC)
            )
        else: 
            updated_data = {
                "device_name": device_name,
                "device_type": device_type,
                "browser": browser,
                "os": os,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "last_login_at": datetime.now(UTC)
            }

            clean_data = {
                key: value for key, value in updated_data.items() if value is not None 
            } 

            return await self.device_repo.update(
                device, 
                **clean_data
            )


    async def get_user_devices(self, user_id: UUID) -> list[UserDevice]:
        """Lấy danh sách tất cả devices của user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Danh sách UserDevice entities.
        """
        return await self.device_repo.get_by_user_id(user_id)


    async def get_device_by_id(self, device_id: UUID, user_id: UUID) -> UserDevice:
        """Lấy device theo ID, đảm bảo thuộc về user.
        
        Args:
            device_id: UUID của device.
            user_id: UUID của user (để verify ownership).
            
        Returns:
            UserDevice entity.
            
        Raises:
            DeviceNotFoundException: Device không tồn tại hoặc không thuộc về user.
        """
        device = await self.device_repo.get_device_by_id(device_id, user_id)

        if not device: 
            raise DeviceNotFoundException()
        
        return device


    async def trust_device(self, device_id: UUID, user_id: UUID) -> UserDevice:
        """Đánh dấu device là trusted.
        
        Trusted devices có thể được cấp token với thời hạn dài hơn
        hoặc bỏ qua 2FA.
        
        Args:
            device_id: UUID của device.
            user_id: UUID của user.
            
        Returns:
            UserDevice đã cập nhật.
        """
        device = await self.get_device_by_id(device_id, user_id)

        return await self.device_repo.set_trusted(device, True)


    async def untrust_device(self, device_id: UUID, user_id: UUID) -> UserDevice:
        """Gỡ trust status của device.
        
        Args:
            device_id: UUID của device.
            user_id: UUID của user.
            
        Returns:
            UserDevice đã cập nhật.
        """
        device = await self.get_device_by_id(device_id, user_id)

        return await self.device_repo.set_trusted(device, False)
    

    async def block_device(self, device_id: UUID, user_id: UUID) -> UserDevice:
        """Block device - không cho phép đăng nhập từ device này.
        
        Args:
            device_id: UUID của device.
            user_id: UUID của user.
            
        Returns:
            UserDevice đã cập nhật.
        """
        device = await self.get_device_by_id(device_id, user_id)

        # Chỉ đổi cờ là chưa đủ: phiên đang chạy trên device đó vẫn refresh được.
        if self.family_repo:
            await self.family_repo.revoke_all_for_device(device.id)

        return await self.device_repo.set_status(device=device, status=DeviceStatus.BLOCKED)
    

    async def unblock_device(self, device_id: UUID, user_id: UUID) -> UserDevice:
        """Gỡ chặn device, đưa về trạng thái active.

        Không có hàm này thì block là một chiều: device bị chặn sẽ không bao giờ
        đăng nhập lại được.
        """
        device = await self.get_device_by_id(device_id, user_id)

        # Không kiểm tra thì endpoint này thành "đặt trạng thái active" chung,
        # kéo cả device đang INACTIVE lên ACTIVE mà API không hề hứa điều đó.
        if device.status != DeviceStatus.BLOCKED:
            return device

        return await self.device_repo.set_status(device=device, status=DeviceStatus.ACTIVE)


    async def remove_device(self, device_id: UUID, user_id: UUID) -> None:
        """Xóa device khỏi danh sách.
        
        Args:
            device_id: UUID của device.
            user_id: UUID của user.
        """
        device = await self.get_device_by_id(device_id, user_id)

        await self.device_repo.delete(device)


    async def remove_all_devices(self, user_id: UUID) -> int:
        """Xóa tất cả devices của user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng devices đã xóa.
        """
        return await self.device_repo.delete_all_by_user(user_id)
    
    
    async def update_device_last_login(self, device: UserDevice) -> UserDevice:
        """Cập nhật thời gian login cuối cùng của device.
        
        Args:
            device: UserDevice entity cần cập nhật.
            
        Returns:
            UserDevice đã cập nhật.
        """
        return await self.device_repo.update_last_login(device)
    

    async def update(self, 
        user_id: UUID, 
        device_id: UUID, 
        update_schema: DeviceUpdate
    ) -> UserDevice: 
        device = await self.get_device_by_id(
            device_id=device_id, 
            user_id=user_id
        )

        update_data = update_schema.model_dump(exclude_unset=True)

        return await self.device_repo.update(
            device, 
            **update_data
        )
    
def get_device_service(
    device_repo: UserDeviceRepoDep,
    family_repo: TokenFamilyRepoDep,
) -> DeviceService:
    """Dependency injection factory cho DeviceService."""
    return DeviceService(device_repo, family_repo)


DeviceServiceDep = Annotated[DeviceService, Depends(get_device_service)]
