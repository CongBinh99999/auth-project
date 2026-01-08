from enum import Enum


class TokenType(str, Enum):
    """Token type constants"""
    ACCESS = "access"   
    REFRESH = "refresh" 
    
    def __str__(self):
        return self.value




class DeviceStatus(str, Enum):
    """Device status constants."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class ErrorMessage(str, Enum):
    """Error message constants."""
    INVALID_CREDENTIALS = "Invalid email or password"
    USER_NOT_FOUND = "User not found"
    USER_INACTIVE = "User account is inactive"
    USER_NOT_VERIFIED = "User email is not verified"
    EMAIL_EXISTS = "Email already registered"
    INVALID_TOKEN = "Invalid or expired token"
    TOKEN_EXPIRED = "Token has expired"
    TOKEN_REVOKED = "Token has been revoked"
    PERMISSION_DENIED = "Permission denied"
    ROLE_NOT_FOUND = "Role not found"


class SuccessMessage(str, Enum):
    """Success message constants."""
    USER_CREATED = "User created successfully"
    USER_VERIFIED = "Email verified successfully"
    PASSWORD_RESET = "Password reset successfully"
    LOGOUT = "Logged out successfully"