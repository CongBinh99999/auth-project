# app/schemas/device.py
# 
# Purpose: Pydantic schemas for UserDevice data transfer.
# 
# Implementation details:
# - DeviceBase: device_name, device_type, browser, os
# - DeviceCreate(DeviceBase): ip_address, user_agent, fingerprint
# - DeviceUpdate: device_name, is_trusted (optional)
# - DeviceResponse(DeviceBase): id, user_id, ip_address, status, is_trusted, 
#                               last_login_at, created_at, updated_at
# - DeviceListResponse: list of DeviceResponse with count
