"""
Module chứa các schemas cho UserDevice entity.

Bao gồm:
- DeviceBase: Base schema chứa các field chung
- DeviceCreate: Schema khi tạo Device mới
- DeviceUpdate: Schema khi cập nhật Device
- DeviceResponse: Schema trả về cho client
- DeviceListResponse: Schema danh sách devices
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

from app.utils.constants import DeviceStatus


class DeviceBase(BaseModel): 
    """Base schema cho Device - chứa các field chung."""
    model_config = ConfigDict(from_attributes=True)
    
    device_name: Optional[str] = Field(None, max_length=255, description="Tên thiết bị")
    device_type: Optional[str] = Field(None, max_length=255, description="Loại thiết bị (desktop, mobile, tablet)")
    browser: Optional[str] = Field(None, max_length=100, description="Trình duyệt")
    os: Optional[str] = Field(None, max_length=100, description="Hệ điều hành")


class DeviceCreate(DeviceBase):
    """Schema khi tạo Device mới."""
    ip_address: Optional[str] = Field(None, max_length=45, description="Địa chỉ IP")
    user_agent: Optional[str] = Field(None, description="User Agent của trình duyệt")
    fingerprint: Optional[str] = Field(None, description="Dấu vân tay thiết bị (device fingerprint)")


class DeviceUpdate(BaseModel): 
    """Schema khi cập nhật thông tin Device."""
    model_config = ConfigDict(from_attributes=True)
    
    device_name: Optional[str] = Field(None, max_length=255, description="Tên thiết bị")
    is_trusted: bool = Field(default=False, description="Đánh dấu thiết bị đáng tin cậy")


class DeviceResponse(DeviceBase): 
    """Schema trả về cho client."""
    id: UUID = Field(..., description="ID của thiết bị")
    user_id: UUID = Field(..., description="ID người dùng sở hữu thiết bị")
    status: DeviceStatus = Field(default="active", description="Trạng thái thiết bị")
    is_trusted: bool = Field(default=False, description="Thiết bị có đáng tin cậy không?")
    last_login_at: datetime = Field(..., description="Thời gian đăng nhập gần nhất")
    created_at: datetime = Field(..., description="Thời gian thêm thiết bị")
    updated_at: datetime = Field(..., description="Thời gian cập nhật gần nhất")


class DeviceListResponse(BaseModel):
    """Schema danh sách thiết bị của người dùng."""
    model_config = ConfigDict(from_attributes=True)
    
    devices: list[DeviceResponse] = Field(default=[], description="Danh sách thiết bị")
    total_count: int = Field(default=0, description="Tổng số thiết bị")
