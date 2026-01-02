from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRole,
    PasswordChange,
)

# Auth schemas
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPayload,
    LogoutRequest,
    LogoutResponse,
    AuthErrorResponse,
    TokenInfo,
    ActiveSessionResponse,
)

# Role schemas
from app.schemas.role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
)

# Device schemas
from app.schemas.device import (
    DeviceBase,
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
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
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
    PasswordResetConfirmResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithRole",
    "PasswordChange",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RegisterResponse",
    "TokenPayload",
    "LogoutRequest",
    "LogoutResponse",
    "AuthErrorResponse",
    "TokenInfo",
    "ActiveSessionResponse",
    # Role
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleWithPermissions",
    "PermissionBase",
    "PermissionCreate",
    "PermissionResponse",
    # Device
    "DeviceBase",
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    "DeviceListResponse",
    # Email Verification
    "EmailVerifyRequest",
    "EmailVerifyResponse",
    "ResendVerificationRequest",
    "ResendVerificationResponse",
    # Password Reset
    "PasswordResetRequest",
    "PasswordResetResponse",
    "PasswordResetConfirm",
    "PasswordResetConfirmResponse",
]
