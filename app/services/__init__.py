"""Service Layer - Business Logic for Authentication System.

This module contains all business logic services for the authentication system.
Services orchestrate multiple repositories and implement complex workflows.

Services:
    - AuthService: Authentication orchestration (register, login, logout)
    - UserService: User profile management
    - RoleService: Role and permission management
    - TokenService: JWT token creation and verification
    - TokenFamilyService: Refresh token rotation management
    - LoginAttemptService: Rate limiting and brute-force protection
    - DeviceService: User device management
    - EmailVerificationService: Email verification workflow
    - PasswordResetService: Password reset workflow
"""

from app.services.auth_service import AuthService, AuthServiceDep
from app.services.device_service import DeviceService, DeviceServiceDep
from app.services.email_verification_service import (
    EmailVerificationService,
    EmailVerificationServiceDep,
)
from app.services.login_attempt_service import (
    LoginAttemptService,
    LoginAttemptServiceDep,
)
from app.services.password_reset_service import (
    PasswordResetService,
    PasswordResetServiceDep,
)
from app.services.role_service import RoleService, RoleServiceDep
from app.services.token_family_service import TokenFamilyService, TokenFamilyServiceDep
from app.services.token_service import TokenBlacklistServiceDep, TokenService
from app.services.user_service import UserService, UserServiceDep

__all__ = [
    # Services
    "AuthService",
    # Dependency Types
    "AuthServiceDep",
    "DeviceService",
    "DeviceServiceDep",
    "EmailVerificationService",
    "EmailVerificationServiceDep",
    "LoginAttemptService",
    "LoginAttemptServiceDep",
    "PasswordResetService",
    "PasswordResetServiceDep",
    "RoleService",
    "RoleServiceDep",
    "TokenBlacklistServiceDep",
    "TokenFamilyService",
    "TokenFamilyServiceDep",
    "TokenService",
    "UserService",
    "UserServiceDep",
]
