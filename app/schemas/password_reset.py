"""
Module chứa các schemas cho Password Reset.

Bao gồm:
- PasswordResetRequest: Request schema yêu cầu đặt lại mật khẩu
- PasswordResetResponse: Response schema cho yêu cầu đặt lại mật khẩu
- PasswordResetConfirm: Request schema xác nhận đặt lại mật khẩu
- PasswordResetConfirmResponse: Response schema xác nhận đặt lại mật khẩu
"""
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class PasswordResetRequest(BaseModel):
    """Request schema cho yêu cầu đặt lại mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="Địa chỉ email để đặt lại mật khẩu")
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Chuẩn hóa email: loại bỏ khoảng trắng và chuyển về chữ thường."""
        return v.strip().lower()


class PasswordResetResponse(BaseModel):
    """Response schema cho yêu cầu đặt lại mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Thông báo kết quả")
    success: bool = Field(default=True, description="Trạng thái gửi email")


class PasswordResetConfirm(BaseModel):
    """Request schema cho xác nhận đặt lại mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    token: str = Field(..., min_length=1, description="Token đặt lại mật khẩu")
    new_password: str = Field(..., min_length=8, max_length=255, description="Mật khẩu mới")
    confirm_password: str = Field(..., min_length=8, max_length=255, description="Xác nhận mật khẩu mới")
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Kiểm tra mật khẩu xác nhận có khớp với mật khẩu mới không."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Mật khẩu xác nhận không khớp với mật khẩu mới")
        return v


class PasswordResetConfirmResponse(BaseModel):
    """Response schema cho xác nhận đặt lại mật khẩu."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Thông báo kết quả")
    success: bool = Field(default=True, description="Trạng thái đặt lại mật khẩu")