# app/repositories/user_device_repository.py
# 
# Purpose: Database access layer for UserDevice operations.
# 
# Implementation details:
# - class UserDeviceRepository:
#     def __init__(self, db: AsyncSession)
#     async def get_by_id(device_id: UUID) -> UserDevice | None
#     async def get_by_user_id(user_id: UUID) -> list[UserDevice]
#     async def get_by_fingerprint(user_id: UUID, fingerprint: str) -> UserDevice | None
#     async def create(device_data) -> UserDevice
#     async def update(device: UserDevice, update_data) -> UserDevice
#     async def update_last_login(device: UserDevice) -> UserDevice
#     async def set_status(device: UserDevice, status: str) -> UserDevice
#     async def set_trusted(device: UserDevice, is_trusted: bool) -> UserDevice
#     async def delete(device: UserDevice) -> None
#     async def delete_all_by_user(user_id: UUID) -> int
