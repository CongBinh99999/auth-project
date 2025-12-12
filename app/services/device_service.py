# app/services/device_service.py
# 
# Purpose: User device management business logic.
# 
# Implementation details:
# - class DeviceService:
#     def __init__(self, db: AsyncSession)
#     async def register_device(user_id: UUID, device_info: dict) -> UserDevice
#     async def get_user_devices(user_id: UUID) -> list[UserDevice]
#     async def get_device(device_id: UUID) -> UserDevice
#     async def update_device(device_id: UUID, update_data) -> UserDevice
#     async def trust_device(device_id: UUID) -> UserDevice
#     async def untrust_device(device_id: UUID) -> UserDevice
#     async def block_device(device_id: UUID) -> UserDevice
#     async def remove_device(device_id: UUID) -> None
#     async def remove_all_devices(user_id: UUID) -> int
#     async def detect_device(user_agent: str, ip_address: str) -> dict
