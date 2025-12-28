from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from typing_extensions import Self

from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """Base schema cho User - chứa các field chung."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    is_active: bool = Field(default=True, description="Is user account active?")


class UserCreate(UserBase):
    """Schema khi tạo User mới - bao gồm password."""
    password: str = Field(..., min_length=8, max_length=255, description="User password")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserUpdate(BaseModel):
    """Schema khi cập nhật User - tất cả field Optional."""
    model_config = ConfigDict(from_attributes=True)
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    is_active: Optional[bool] = Field(None, description="Is user account active?")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().lower()
        return v


class UserResponse(UserBase):
    """Schema trả về cho client."""
    id: UUID
    email_verified: bool = Field(default=False, description="Is email verified?")
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserWithRole(UserResponse):
    """User kèm thông tin Role."""
    role: Optional[RoleResponse] = None


class PasswordChange(BaseModel):
    """Schema để đổi mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    old_password: str = Field(..., min_length=8, max_length=255, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=255, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=255, description="Confirm new password")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Mật khẩu xác nhận không khớp với mật khẩu mới")
        return v
