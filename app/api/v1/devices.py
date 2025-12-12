# app/api/v1/devices.py
# 
# Purpose: User device management endpoints.
# 
# Implementation details:
# - router = APIRouter(prefix="/devices", tags=["Devices"])
# - GET / -> DeviceController.get_my_devices
# - GET /{device_id} -> DeviceController.get_device
# - PUT /{device_id} -> DeviceController.update_device
# - POST /{device_id}/trust -> DeviceController.trust_device
# - DELETE /{device_id}/trust -> DeviceController.untrust_device
# - DELETE /{device_id} -> DeviceController.remove_device
# - DELETE / -> DeviceController.remove_all_devices
# - Dependencies: DbSession, ActiveUser
