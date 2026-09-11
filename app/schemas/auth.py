"""
Module chứa các schemas cho Authentication.

Bao gồm:
- LoginRequest, RegisterRequest: Request schemas cho đăng nhập/đăng ký
- RefreshTokenRequest, LogoutRequest: Request schemas cho refresh/logout
- TokenResponse, RegisterResponse, LogoutResponse: Response schemas
- TokenPayload, TokenInfo: Schemas cho JWT token
- ActiveSessionResponse: Schema cho danh sách phiên đăng nhập
"""
import uuid
from datetime import UTC, datetime
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.utils.constants import TokenType


class LoginRequest(BaseModel):
    """Request schema cho đăng nhập người dùng."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="Địa chỉ email của người dùng")
    password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu người dùng")
    device_info: str | None = Field(None, max_length=500, description="Thông tin thiết bị để theo dõi phiên đăng nhập")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Chuẩn hóa email: loại bỏ khoảng trắng và chuyển về chữ thường."""
        return v.strip().lower()


class RegisterRequest(BaseModel):
    """Request schema cho đăng ký người dùng mới."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="Địa chỉ email của người dùng")
    password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu người dùng")
    confirm_password: str = Field(..., min_length=8, max_length=255, description="Xác nhận mật khẩu")
    full_name: str | None = Field(None, min_length=1, max_length=255, description="Họ và tên đầy đủ")

    @model_validator(mode='before')
    @classmethod
    def pre_process_data(cls, data: Any) -> Any:
        """Chuẩn hóa dữ liệu đầu vào trước khi validate."""
        if isinstance(data, dict):
            if data.get("email"):
                data["email"] = data["email"].strip().lower()
            if data.get("password"):
                data["password"] = data["password"].strip()
            if data.get("confirm_password"):
                data["confirm_password"] = data["confirm_password"].strip()
            if data.get("full_name"):
                data["full_name"] = data["full_name"].strip()
        return data

    @model_validator(mode='after')
    def validate_passwords_match(self) -> Self:
        """Kiểm tra mật khẩu có khớp với mật khẩu xác nhận không."""
        if self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp với nhau")
        return self


class RefreshTokenRequest(BaseModel):
    """Request schema cho làm mới token."""
    model_config = ConfigDict(from_attributes=True)
    
    refresh_token: str = Field(..., min_length=1, description="Refresh token để lấy access token mới")


class LogoutRequest(BaseModel):
    """Request schema cho đăng xuất."""
    model_config = ConfigDict(from_attributes=True)
    
    refresh_token: str | None = Field(None, description="Refresh token cần vô hiệu hóa")
    logout_all_devices: bool = Field(default=False, description="Đăng xuất khỏi tất cả thiết bị")


class TokenResponse(BaseModel):
    """Response schema chứa các token xác thực."""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Loại token")
    refresh_token: str = Field(..., description="JWT refresh token để làm mới token")
    expires_in: int | None = Field(None, description="Thời gian hết hạn access token (giây)")


class RegisterResponse(BaseModel):
    """Response schema sau khi đăng ký thành công."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Thông báo kết quả")
    user_id: uuid.UUID = Field(..., description="ID người dùng vừa tạo")
    email: EmailStr = Field(..., description="Địa chỉ email đã đăng ký")
    requires_verification: bool = Field(default=True, description="Có cần xác thực email không?")


class LogoutResponse(BaseModel):
    """Response schema sau khi đăng xuất thành công."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(default="Đăng xuất thành công", description="Thông báo kết quả")
    success: bool = Field(default=True, description="Trạng thái đăng xuất")


class AuthErrorResponse(BaseModel):
    """Response schema cho lỗi xác thực."""
    model_config = ConfigDict(from_attributes=True)
    
    error: str = Field(..., description="Loại lỗi")
    message: str = Field(..., description="Thông báo lỗi")
    detail: str | None = Field(None, description="Chi tiết lỗi")


class TokenPayload(BaseModel):
    """Schema biểu diễn cấu trúc payload của JWT token."""
    model_config = ConfigDict(from_attributes=True)
    
    sub: uuid.UUID = Field(..., description="Subject - ID người dùng")
    jti: uuid.UUID = Field(..., description="JWT ID - Mã định danh token duy nhất")
    type: TokenType = Field(default=TokenType.ACCESS, description="Loại token (access/refresh)")
    family_id: uuid.UUID | None = Field(None, description="ID nhóm token cho refresh token rotation")
    iat: datetime = Field(..., description="Thời gian phát hành token")
    exp: datetime = Field(..., description="Thời gian hết hạn token")
    
    @property
    def is_expired(self) -> bool:
        """Kiểm tra token đã hết hạn chưa."""
        return datetime.now(UTC) > self.exp


class TokenInfo(BaseModel):
    """Schema cho thông tin token hiển thị."""
    model_config = ConfigDict(from_attributes=True)
    
    token_id: uuid.UUID = Field(..., description="ID của token")
    user_id: uuid.UUID = Field(..., description="ID người dùng")
    token_type: TokenType = Field(..., description="Loại token")
    issued_at: datetime = Field(..., description="Thời gian phát hành")
    expires_at: datetime = Field(..., description="Thời gian hết hạn")
    is_revoked: bool = Field(default=False, description="Token đã bị thu hồi chưa?")


class ActiveSessionResponse(BaseModel):
    """Schema cho danh sách phiên đăng nhập đang hoạt động."""
    model_config = ConfigDict(from_attributes=True)
    
    sessions: list[TokenInfo] = Field(default=[], description="Danh sách phiên đăng nhập")
    total_count: int = Field(default=0, description="Tổng số phiên đang hoạt động")