"""
Module chứa các schemas cho Role và Permission entities.

Bao gồm:
- RoleBase, RoleCreate, RoleUpdate, RoleResponse: Schemas cho Role
- RoleWithPermissions: Role kèm danh sách permissions
- PermissionBase, PermissionCreate, PermissionResponse: Schemas cho Permission
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel): 
    """Base schema cho Role - chứa các field chung."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=255, description="Tên vai trò")
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        pattern=r"^[A-Z][A-Z0-9_]*$", 
        description="Mã định danh vai trò (VD: ADMIN, USER, MODERATOR)"
    )
    description: str | None = Field(None, max_length=500, description="Mô tả vai trò")


class RoleCreate(RoleBase): 
    """Schema khi tạo Role mới."""
    model_config = ConfigDict(from_attributes=True)

    is_default: bool = Field(default=False, description="Có phải vai trò mặc định không?")
    is_system: bool = Field(default=False, description="Có phải vai trò hệ thống không?")


class RoleUpdate(BaseModel): 
    """Schema khi cập nhật Role - tất cả field Optional."""
    model_config = ConfigDict(from_attributes=True)
    
    name: str | None = Field(None, min_length=2, max_length=255, description="Tên vai trò")
    code: str | None = Field(None, min_length=1, max_length=50, pattern=r"^[A-Z][A-Z0-9_]*$", description="Mã định danh vai trò")
    description: str | None = Field(None, max_length=500, description="Mô tả vai trò")
    is_default: bool | None = Field(None, description="Có phải vai trò mặc định không?")
    is_system: bool | None = Field(None, description="Có phải vai trò hệ thống không?")


class RoleResponse(RoleBase):
    """Schema trả về cho client."""
    id: UUID = Field(..., description="ID của vai trò")
    is_default: bool = Field(..., description="Có phải vai trò mặc định không?")
    is_system: bool = Field(..., description="Có phải vai trò hệ thống không?")
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: datetime | None = Field(None, description="Thời gian cập nhật gần nhất")


class RoleWithPermissions(RoleResponse):
    """Role kèm danh sách permissions."""
    permissions: list[PermissionResponse] = Field(default=[], description="Danh sách quyền của vai trò")


class PermissionBase(BaseModel):
    """Base schema cho Permission - chứa các field chung."""
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1, max_length=255, description="Tên quyền")
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        pattern=r"^[a-z][a-z0-9_:]*$",
        description="Mã quyền (VD: user:read, user:write)"
    )
    description: str | None = Field(None, max_length=500, description="Mô tả quyền")
    module: str = Field(..., min_length=1, max_length=100, description="Tên module (VD: user, role)")


class PermissionCreate(PermissionBase):
    """Schema khi tạo Permission mới."""


class PermissionResponse(PermissionBase):
    """Schema trả về cho client."""
    id: UUID = Field(..., description="ID của quyền")
    created_at: datetime = Field(..., description="Thời gian tạo")


# Rebuild model để resolve forward reference
RoleWithPermissions.model_rebuild()