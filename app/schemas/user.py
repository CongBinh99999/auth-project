"""
Module chứa các schemas cho User entity.

Bao gồm:
- UserBase: Base schema chứa các field chung
- UserCreate: Schema khi tạo User mới
- UserUpdate: Schema khi cập nhật User
- UserResponse: Schema trả về cho client
- UserWithRole: User kèm thông tin Role
- PasswordChange: Schema để đổi mật khẩu
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """Base schema cho User - chứa các field chung."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="Địa chỉ email của người dùng")
    full_name: str | None = Field(None, min_length=1, max_length=255, description="Họ và tên đầy đủ")
    is_active: bool = Field(default=True, description="Tài khoản có đang hoạt động không?")


class UserCreate(UserBase):
    """Schema khi tạo User mới - bao gồm password."""
    password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu người dùng")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Chuẩn hóa email: loại bỏ khoảng trắng và chuyển về chữ thường."""
        return v.strip().lower()


class UserUpdate(BaseModel):
    """Schema khi cập nhật User - tất cả field Optional."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr | None = Field(None, description="Địa chỉ email của người dùng")
    full_name: str | None = Field(None, min_length=1, max_length=255, description="Họ và tên đầy đủ")
    is_active: bool | None = Field(None, description="Tài khoản có đang hoạt động không?")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        """Chuẩn hóa email nếu có giá trị."""
        if v is not None:
            return v.strip().lower()
        return v


class UserResponse(UserBase):
    """Schema trả về cho client."""
    id: UUID = Field(..., description="ID của người dùng")
    is_verified: bool = Field(default=False, description="Email đã được xác thực chưa?")
    created_at: datetime = Field(..., description="Thời gian tạo tài khoản")
    updated_at: datetime | None = Field(None, description="Thời gian cập nhật gần nhất")


class UserWithRole(UserResponse):
    """User kèm thông tin Role."""
    role: RoleResponse | None = Field(None, description="Vai trò của người dùng")


class PasswordChange(BaseModel):
    """Schema để đổi mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    old_password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu hiện tại")
    new_password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu mới")
    confirm_password: str = Field(..., min_length=8, max_length=255, description="Xác nhận mật khẩu mới")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Kiểm tra mật khẩu xác nhận có khớp với mật khẩu mới không."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Mật khẩu xác nhận không khớp với mật khẩu mới")
        return v
