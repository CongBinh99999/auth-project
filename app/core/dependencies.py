"""
FastAPI Dependencies cho Authentication và RBAC.

Module này chứa các dependencies để:
- Extract token từ request header
- Lấy current user từ token
- Kiểm tra user có active/verified không
- RBAC: Kiểm tra role và permission
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserNotFoundException,
)
from app.models.user import User
from app.repositories import UserRepoDep
from app.services.token_service import TokenBlacklistServiceDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 
# nếu có sử dụng cho khách tham số "auto_error=False" oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin", auto_error=False)
# nếu không sử dụng oauth2 thì sử header từ fastapi bằng None (nhưng không nên chọn) 


DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    token_service: TokenBlacklistServiceDep,
    user_repo: UserRepoDep
) -> User:
    """
    Dependency để lấy current user từ JWT token.
    
    Flow:
        1. Extract token từ Authorization header (oauth2_scheme)
        2. Verify token hợp lệ và chưa bị blacklist (token_service.verify_token)
        3. Lấy user từ database theo payload.sub (user_repo.get_by_id)
    
    Args:
        token: JWT token string từ header.
        token_service: Service để verify token.
        user_repo: Repository để query user.
        
    Returns:
        User: User object nếu token hợp lệ.
        
    Raises:
        HTTPException 401: Token không hợp lệ, expired, hoặc user không tồn tại.
    
    Implementation hints:
        - Sử dụng token_service.verify_token(token) -> TokenPayload
        - Bắt InvalidTokenException, TokenExpiredException
        - user_repo.get_by_id(payload.sub)
    """
    try:
        payload = await token_service.verify_token(token)
    except (InvalidTokenException, TokenExpiredException) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ hoặc đã hết hạn") from e

    user = await user_repo.get_by_id(payload.sub) 

    if not user: 
        raise UserNotFoundException()
    
    return user




async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency để lấy current user và đảm bảo user đang active.
    
    Args:
        current_user: User object từ get_current_user dependency.
        
    Returns:
        User: User object nếu user.is_active == True.
        
    Raises:
        HTTPException 403: User bị inactive.
    """
    if not current_user.is_active: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User bị inactive")
    
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Dependency để lấy user đã verified email.
    
    Args:
        current_user: User object từ get_current_active_user dependency.
        
    Returns:
        User: User object nếu user.is_verified == True.
        
    Raises:
        HTTPException 403: Email chưa được verify.
    """
    if not current_user.is_verified: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email chưa được verify")
    
    return current_user

CurrentUser = Annotated[User, Depends(get_current_user)]

ActiveUser = Annotated[User, Depends(get_current_active_user)]

VerifiedUser = Annotated[User, Depends(get_current_verified_user)]


def require_permission(permission_code: str):
    """
    Factory function tạo dependency kiểm tra user có permission cụ thể.
    
    Usage trong route:
        @router.get("/admin/users", dependencies=[Depends(require_permission("users:read"))])
        async def list_users(): ...
    
    Args:
        permission_code: Mã permission cần kiểm tra (vd: "users:read", "roles:write").
        
    Returns:
        Dependency function kiểm tra permission.
        
    Raises:
        HTTPException 403: User không có permission.
    
    Implementation hints:
        - Lấy user.role.permissions
        - Check permission_code có trong danh sách không
    """
    async def permission_checker(current_user: ActiveUser):
        if current_user.role and current_user.role.permissions: 
            permission_codes = [perm.code for perm in current_user.role.permissions]
            if permission_code not in permission_codes:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập")
        else: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập")
        return current_user
    
    return permission_checker


def require_role(role_code: str):
    """
    Factory function tạo dependency kiểm tra user có role cụ thể.
    
    Usage trong route:
        @router.delete("/users/{id}", dependencies=[Depends(require_role("admin"))])
        async def delete_user(): ...
    
    Args:
        role_code: Mã role cần kiểm tra (vd: "admin", "moderator").
        
    Returns:
        Dependency function kiểm tra role.
        
    Raises:
        HTTPException 403: User không có role yêu cầu.
    
    Implementation hints:
        - So sánh user.role.code với role_code
    """
    async def role_checker(current_user: ActiveUser):
        if current_user.role:
            if role_code != current_user.role.code:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User không có role yêu cầu.")
        else: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User không có role yêu cầu.")
        return current_user
    
    return role_checker


def require_any_role(role_codes: list[str]):
    """
    Factory function tạo dependency kiểm tra user có MỘT TRONG các roles.
    
    Usage trong route:
        @router.get("/dashboard", dependencies=[Depends(require_any_role(["admin", "moderator"]))])
        async def dashboard(): ...
    
    Args:
        role_codes: Danh sách mã roles được phép.
        
    Returns:
        Dependency function kiểm tra role.
        
    Raises:
        HTTPException 403: User không có role nào trong danh sách.
    """
    async def role_checker(current_user: ActiveUser):
        if current_user.role and current_user.role.code in role_codes:
            return current_user
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User không có role nào trong danh sách."
        )
    
    return role_checker

RequireAdmin = Depends(require_role("admin"))
