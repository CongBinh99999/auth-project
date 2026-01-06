"""Password Reset Service - Password reset workflow.

Quản lý quy trình đặt lại mật khẩu qua email.
"""

from uuid import UUID
from typing import Annotated
from fastapi import Depends
from datetime import datetime, timedelta, timezone 

from app.repositories.password_reset_repository import(
    PasswordResetRepository,
    PasswordResetRepoDep
)

from app.repositories.user_repository import (
    UserRepository,
    UserRepoDep
)

from app.repositories.token_family_repository import (
    TokenFamilyRepository,
    TokenFamilyRepoDep
)

from app.models.password_reset_token import PasswordResetToken

from app.core.security import (
    generate_verification_token,
    hash_verification_token,
    hash_password
)

from app.core.exceptions import (
    TokenExpiredException, 
    InvalidTokenException
)

from app.config.settings import get_settings

setting = get_settings()


class PasswordResetService:
    """Service quản lý đặt lại mật khẩu.
    
    Workflow:
    1. User quên mật khẩu → request_reset() → gửi email với token
    2. User click link → validate_token() → hiển thị form đổi mật khẩu
    3. User submit → reset_password() → cập nhật password + revoke all sessions
    
    Security:
    - Token được lưu dưới dạng hash
    - Mỗi token chỉ dùng được một lần
    - Token có thời hạn (configurable)
    - Sau khi đổi mật khẩu, tất cả sessions bị revoke
    
    Attributes:
        user_repo: Repository để lấy user và cập nhật password.
        reset_repo: Repository để quản lý reset tokens.
        family_repo: Repository để revoke sessions sau khi đổi password.
    """

    def __init__(
        self, 
        user_repo: UserRepository, 
        reset_repo: PasswordResetRepository, 
        family_repo: TokenFamilyRepository
    ):
        self.user_repo = user_repo
        self.reset_repo = reset_repo
        self.family_repo = family_repo

    
    async def request_reset(self, email: str) -> str | None:
        """Yêu cầu reset password.
        
        SECURITY NOTE: Luôn trả về None thay vì raise exception
        khi email không tồn tại để không reveal user exists.
        
        Flow:
        1. Tìm user theo email
        2. Xóa token cũ (nếu có)
        3. Tạo token mới
        4. Return plain token để gửi email
        
        Args:
            email: Email của user cần reset password.
            
        Returns:
            Plain token string nếu user tồn tại, None nếu không.
        """
        user = await self.user_repo.get_by_email(email)

        if not user: 
            return None 
        
        await self.reset_repo.delete_by_user(user.id)

        plain_token, hashed_token = generate_verification_token()

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=setting.PASSWORD_RESET_EXPIRE_MINUTES)

        await self.reset_repo.create(
            user_id=user.id, 
            token_hash=hashed_token, 
            expires_at=expires_at
        )

        return plain_token

        
    async def validate_token(self, token: str) -> PasswordResetToken | None:
        """Validate reset token.
        
        Kiểm tra token chưa sử dụng và chưa hết hạn.
        
        Args:
            token: Plain token từ email link.
            
        Returns:
            PasswordResetToken entity nếu hợp lệ, None nếu không.
        """
        hashed_token = hash_verification_token(token)

        reset_token = await self.reset_repo.get_by_token_hash(hashed_token)
        if not reset_token: 
            return None 
        
        if reset_token.used_at is not None: 
            return None  
               
        if reset_token.expires_at < datetime.now(timezone.utc): 
            return None     

        return reset_token
        

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Đặt lại mật khẩu người dùng.
        
        Flow:
        1. Validate token
        2. Lấy user từ token
        3. Hash new password
        4. Update user password
        5. Mark token as used
        6. Revoke all sessions (force re-login)
        
        Args:
            token: Plain reset token từ email.
            new_password: Mật khẩu mới.
            
        Returns:
            True nếu thành công.
            
        Raises:
            InvalidTokenException: Token không hợp lệ hoặc đã sử dụng.
        """
        reset_token = await self.validate_token(token)
        if reset_token is None: 
            raise InvalidTokenException()
        
        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            raise InvalidTokenException()
        
        hashed_password = hash_password(new_password)

        await self.user_repo.update_password(user, hashed_password)

        await self.reset_repo.mark_used(reset_token)

        await self.family_repo.revoke_all_for_user(reset_token.user_id)

        return True


    async def cleanup_expired_tokens(self) -> int:
        """Xóa các reset tokens đã hết hạn.
        
        Nên chạy định kỳ để dọn dẹp database.
        
        Returns:
            Số lượng tokens đã xóa.
        """
        return await self.reset_repo.cleanup_expired()


def get_password_reset_service(
    user_repo: UserRepoDep,
    reset_repo: PasswordResetRepoDep, 
    family_repo: TokenFamilyRepoDep
) -> PasswordResetService:
    """Dependency injection factory cho PasswordResetService."""
    return PasswordResetService(user_repo, reset_repo, family_repo)


PasswordResetServiceDep = Annotated[PasswordResetService, Depends(get_password_reset_service)]
