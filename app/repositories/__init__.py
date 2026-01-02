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

from app.repositories.user_repository import (
    UserRepository,
    UserRepoDep,
    get_user_repository,
)

from app.repositories.role_repository import (
    RoleRepository,
    RoleRepoDep,
    get_role_repository,
)

from app.repositories.permission_repository import (
    PermissionRepository,
    PermissionRepoDep,
    get_permission_repository,
)

from app.repositories.user_device_repository import (
    UserDeviceRepository,
    UserDeviceRepoDep,
    get_user_device_repository,
)

from app.repositories.token_family_repository import (
    TokenFamilyRepository,
    TokenFamilyRepoDep,
    get_token_family_repository,
)

from app.repositories.token_blacklist_repository import (
    TokenBlacklistRepository,
    TokenBlacklistRepoDep,
    get_token_blacklist_repository,
)

from app.repositories.login_attempt_repository import (
    LoginAttemptRepository,
    LoginAttemptRepoDep,
    get_login_attempt_repository,
)

from app.repositories.email_verification_repository import (
    EmailVerificationRepository,
    EmailVerificationRepoDep,
    get_email_verification_repository,
)

from app.repositories.password_reset_repository import (
    PasswordResetRepository,
    PasswordResetRepoDep,
    get_password_reset_repository,
)


__all__ = [
    # User
    "UserRepository",
    "UserRepoDep",
    "get_user_repository",
    # Role
    "RoleRepository",
    "RoleRepoDep",
    "get_role_repository",
    # Permission
    "PermissionRepository",
    "PermissionRepoDep",
    "get_permission_repository",
    # UserDevice
    "UserDeviceRepository",
    "UserDeviceRepoDep",
    "get_user_device_repository",
    # TokenFamily
    "TokenFamilyRepository",
    "TokenFamilyRepoDep",
    "get_token_family_repository",
    # TokenBlacklist
    "TokenBlacklistRepository",
    "TokenBlacklistRepoDep",
    "get_token_blacklist_repository",
    # LoginAttempt
    "LoginAttemptRepository",
    "LoginAttemptRepoDep",
    "get_login_attempt_repository",
    # EmailVerification
    "EmailVerificationRepository",
    "EmailVerificationRepoDep",
    "get_email_verification_repository",
    # PasswordReset
    "PasswordResetRepository",
    "PasswordResetRepoDep",
    "get_password_reset_repository",
]
