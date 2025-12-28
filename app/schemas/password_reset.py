from pydantic import BaseModel, Field, ConfigDict, EmailStr


class PasswordResetRequest(BaseModel):
    """Request schema for initiating password reset."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="User email address for password reset")


class PasswordResetResponse(BaseModel):
    """Response schema for password reset request."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., min_length=1, description="Response message")


class PasswordResetConfirm(BaseModel):  # ← Sửa lỗi chính tả
    """Request schema for confirming password reset."""
    model_config = ConfigDict(from_attributes=True)
    
    token: str = Field(..., min_length=1, description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=255, description="New password")


class PasswordResetConfirmResponse(BaseModel):
    """Response schema for password reset confirmation."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., min_length=1, description="Response message")
    success: bool = Field(default=False, description="Password reset success status")