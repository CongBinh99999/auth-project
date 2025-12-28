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
from typing import Optional
from pydantic import BaseModel, Field
import uuid
from app.utils.constants import DeviceStatus
from datetime import datetime

class DeviceBase(BaseModel): 
    device_name: Optional[str] = Field(max_length=255)
    device_type: Optional[str] = Field(max_length=255)
    browser: Optional[str] = Field(max_length=100)
    os: Optional[str] = Field(max_length=100)

class DeviceCreate(DeviceBase):
    ip_address: Optional[str] = Field(max_length=45)
    user_agent: Optional[str]
    fingerprint: Optional[str]

class DeviceUpdate(BaseModel): 
    device_name: Optional[str] = Field(max_length=255)
    is_trusted: bool = False

class DeviceResponse(DeviceBase): 
    id: uuid.UUID
    user_id: uuid.UUID
    status: DeviceStatus = "active"
    is_trusted: bool = False
    last_login_at: datetime
    created_at: datetime 
    updated_at: datetime

class DeviceListResponse(BaseModel):
    device: list[DeviceResponse]



