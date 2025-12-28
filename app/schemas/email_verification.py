from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator


class EmailVerifyRequest(BaseModel):
    """Request schema for email verification."""
    model_config = ConfigDict(from_attributes=True)
    
    token: str = Field(..., min_length=1, description="Email verification token")


class EmailVerifyResponse(BaseModel):
    """Response schema for email verification."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., min_length=1, description="Response message")
    verified: bool = Field(default=False, description="Email verification status")


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email."""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResendVerificationResponse(BaseModel):
    """Response schema for resend verification."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(..., min_length=1, description="Response message")