"""
Module chứa các schemas cho Email Verification.

Bao gồm:
- EmailVerifyRequest: Request schema cho xác thực email
- EmailVerifyResponse: Response schema cho xác thực email
- ResendVerificationRequest: Request schema gửi lại email xác thực
- ResendVerificationResponse: Response schema gửi lại email xác thực
"""
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator


class EmailVerifyRequest(BaseModel):
    """Request schema cho xác thực email."""
    model_config = ConfigDict(from_attributes=True)
    
    token: str = Field(..., min_length=1, description="Token xác thực email")


class EmailVerifyResponse(BaseModel):
    """Response schema cho xác thực email."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Thông báo kết quả")
    verified: bool = Field(default=False, description="Trạng thái xác thực email")


class ResendVerificationRequest(BaseModel):
    """Request schema cho gửi lại email xác thực."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="Địa chỉ email cần gửi lại xác thực")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Chuẩn hóa email: loại bỏ khoảng trắng và chuyển về chữ thường."""
        return v.strip().lower()


class ResendVerificationResponse(BaseModel):
    """Response schema cho gửi lại email xác thực."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., description="Thông báo kết quả")
    success: bool = Field(default=True, description="Trạng thái gửi email")