# app/controllers/device_controller.py
# 
# Purpose: Controller for User Device management operations.
# 
# Implementation details:
# - class DeviceController:
#     def __init__(self, db: AsyncSession)
#     async def get_my_devices(user: User) -> list[DeviceResponse]
#     async def get_device(user: User, device_id: UUID) -> DeviceResponse
#     async def update_device(user: User, device_id: UUID, data: DeviceUpdate) -> DeviceResponse
#     async def trust_device(user: User, device_id: UUID) -> DeviceResponse
#     async def untrust_device(user: User, device_id: UUID) -> DeviceResponse
#     async def remove_device(user: User, device_id: UUID) -> dict
#     async def remove_all_devices(user: User) -> dict
