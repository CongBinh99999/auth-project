# Auth schemas
from app.schemas.auth import (
    ActiveSessionResponse,
    AuthErrorResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenInfo,
    TokenPayload,
    TokenResponse,
)

# Device schemas
from app.schemas.device import (
    DeviceBase,
    DeviceCreate,
    DeviceListResponse,
    DeviceResponse,
    DeviceUpdate,
)

# Email Verification schemas
from app.schemas.email_verification import (
    EmailVerifyRequest,
    EmailVerifyResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
)

# Password Reset schemas
from app.schemas.password_reset import (
    PasswordResetConfirm,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetResponse,
)

# Role schemas
from app.schemas.role import (
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
    RoleBase,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleWithPermissions,
)
from app.schemas.user import (
    PasswordChange,
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithRole,
)

__all__ = [
    "ActiveSessionResponse",
    "AuthErrorResponse",
    # Device
    "DeviceBase",
    "DeviceCreate",
    "DeviceListResponse",
    "DeviceResponse",
    "DeviceUpdate",
    # Email Verification
    "EmailVerifyRequest",
    "EmailVerifyResponse",
    # Auth
    "LoginRequest",
    "LogoutRequest",
    "LogoutResponse",
    "PasswordChange",
    "PasswordResetConfirm",
    "PasswordResetConfirmResponse",
    # Password Reset
    "PasswordResetRequest",
    "PasswordResetResponse",
    "PermissionBase",
    "PermissionCreate",
    "PermissionResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RegisterResponse",
    "ResendVerificationRequest",
    "ResendVerificationResponse",
    # Role
    "RoleBase",
    "RoleCreate",
    "RoleResponse",
    "RoleUpdate",
    "RoleWithPermissions",
    "TokenInfo",
    "TokenPayload",
    "TokenResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserWithRole",
]
