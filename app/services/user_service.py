"""User Service - User profile management.

Quản lý thông tin người dùng bao gồm xem profile, cập nhật thông tin,
và đổi mật khẩu.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.core.exceptions import (
    EmailExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.token_family_repository import (
    TokenFamilyRepoDep,
    TokenFamilyRepository,
)
from app.repositories.user_repository import UserRepoDep, UserRepository
from app.schemas.user import UserResponse


class UserService:
    """Service quản lý thông tin người dùng.
    
    Cung cấp các chức năng:
    - Xem profile người dùng
    - Cập nhật thông tin profile
    - Đổi mật khẩu
    
    Attributes:
        user_repo: Repository để thao tác với User entity.
        token_family_repo: Repository để revoke sessions khi đổi password.
    """

    def __init__(self, 
        user_repo: UserRepository, 
        token_family_repo: TokenFamilyRepository
    ): 
        self.user_repo = user_repo
        self.token_family_repo = token_family_repo


    async def update_user_profile(
        self, 
        user_id: UUID, 
        email: str | None = None,
        full_name: str | None = None,
        is_active: bool | None = None
    ) -> UserResponse:
        """Cập nhật thông tin profile của user.
        
        Chỉ cập nhật các field được truyền vào (không None).
        Nếu thay đổi email, kiểm tra email mới chưa được sử dụng.
        
        Args:
            user_id: UUID của user cần cập nhật.
            email: Email mới (optional).
            full_name: Tên đầy đủ mới (optional).
            is_active: Trạng thái active mới (optional).
            
        Returns:
            UserResponse chứa thông tin đã cập nhật.
            
        Raises:
            UserNotFoundException: User không tồn tại.
            EmailExistsException: Email mới đã được sử dụng.
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user: 
            raise UserNotFoundException()
        
        if email and email != user.email:
            existing = await self.user_repo.get_by_email(email)
            if existing: 
                raise EmailExistsException()
        
        update_data = {
            k: v for k, v in {
                "email": email,
                "full_name": full_name,
                "is_active": is_active
            }.items() if v is not None
        }
            
        updated_user = await self.user_repo.update(user, **update_data)
        return UserResponse.model_validate(updated_user)


    async def change_password(self, user: User, old_password: str, new_password: str) -> None:
        """Đổi mật khẩu người dùng.
        
        Sau khi đổi mật khẩu thành công, tất cả sessions của user sẽ bị revoke
        để bảo mật (force re-login trên tất cả devices).
        
        Args:
            user: User entity cần đổi mật khẩu.
            old_password: Mật khẩu cũ để xác thực.
            new_password: Mật khẩu mới.
            
        Raises:
            InvalidCredentialsException: Mật khẩu cũ không đúng.
        """
        if not verify_password(old_password, user.hashed_password): 
            raise InvalidCredentialsException()
        
        hashed = hash_password(new_password)
        await self.user_repo.update_password(user, hashed)

        await self.token_family_repo.revoke_all_for_user(user.id) 
        

def get_user_service(
    user_repo: UserRepoDep, 
    token_family_repo: TokenFamilyRepoDep
) -> UserService:
    """Dependency injection factory cho UserService."""
    return UserService(user_repo, token_family_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]