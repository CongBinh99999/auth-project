"""
Repository module - Data Access Layer cho ứng dụng.

Module này chứa các repository classes để thao tác với database.
Mỗi repository chịu trách nhiệm CRUD operations cho một entity cụ thể.

Exports:
    - UserRepository, UserRepoDep
    - RoleRepository, RoleRepoDep
    - PermissionRepository, PermissionRepoDep
    - UserDeviceRepository, UserDeviceRepoDep
    - TokenFamilyRepository, TokenFamilyRepoDep
    - TokenBlacklistRepository, TokenBlacklistRepoDep
    - LoginAttemptRepository, LoginAttemptRepoDep
    - EmailVerificationRepository, EmailVerificationRepoDep
    - PasswordResetRepository, PasswordResetRepoDep
"""

from app.repositories.email_verification_repository import (
    EmailVerificationRepoDep,
    EmailVerificationRepository,
    get_email_verification_repository,
)
from app.repositories.login_attempt_repository import (
    LoginAttemptRepoDep,
    LoginAttemptRepository,
    get_login_attempt_repository,
)
from app.repositories.password_reset_repository import (
    PasswordResetRepoDep,
    PasswordResetRepository,
    get_password_reset_repository,
)
from app.repositories.permission_repository import (
    PermissionRepoDep,
    PermissionRepository,
    get_permission_repository,
)
from app.repositories.role_repository import (
    RoleRepoDep,
    RoleRepository,
    get_role_repository,
)
from app.repositories.token_blacklist_repository import (
    TokenBlacklistRepoDep,
    TokenBlacklistRepository,
    get_token_blacklist_repository,
)
from app.repositories.token_family_repository import (
    TokenFamilyRepoDep,
    TokenFamilyRepository,
    get_token_family_repository,
)
from app.repositories.user_device_repository import (
    UserDeviceRepoDep,
    UserDeviceRepository,
    get_user_device_repository,
)
from app.repositories.user_repository import (
    UserRepoDep,
    UserRepository,
    get_user_repository,
)

__all__ = [
    "EmailVerificationRepoDep",
    # EmailVerification
    "EmailVerificationRepository",
    "LoginAttemptRepoDep",
    # LoginAttempt
    "LoginAttemptRepository",
    "PasswordResetRepoDep",
    # PasswordReset
    "PasswordResetRepository",
    "PermissionRepoDep",
    # Permission
    "PermissionRepository",
    "RoleRepoDep",
    # Role
    "RoleRepository",
    "TokenBlacklistRepoDep",
    # TokenBlacklist
    "TokenBlacklistRepository",
    "TokenFamilyRepoDep",
    # TokenFamily
    "TokenFamilyRepository",
    "UserDeviceRepoDep",
    # UserDevice
    "UserDeviceRepository",
    "UserRepoDep",
    # User
    "UserRepository",
    "get_email_verification_repository",
    "get_login_attempt_repository",
    "get_password_reset_repository",
    "get_permission_repository",
    "get_role_repository",
    "get_token_blacklist_repository",
    "get_token_family_repository",
    "get_user_device_repository",
    "get_user_repository",
]
