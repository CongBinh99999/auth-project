from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(detail="Token has expired")


class TokenRevokedException(AuthException):
    def __init__(self):
        super().__init__(detail="Token has been revoked")


class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid or expired token")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class UserInactiveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )


class UserNotVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User email is not verified",
        )


class EmailExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class PermissionNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )




class RoleNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )


class CodeRoleExistsException(HTTPException):
    def __init__(self): 
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Code Role already"
        )


class DeviceNotFoundException(HTTPException): 
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= "Device Not found"
        )


class TooManyLoginAttemptsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Login too many"
        )