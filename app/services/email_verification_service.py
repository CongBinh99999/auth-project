"""Email Verification Service - Email verification workflow.

Quản lý quy trình xác thực email người dùng sau khi đăng ký.
"""

from uuid import UUID
from typing import Annotated
from fastapi import Depends
from datetime import datetime, timezone, timedelta

from app.repositories.user_repository import (
    UserRepository, 
    UserRepoDep
)

from app.repositories.email_verification_repository import (
    EmailVerificationRepoDep, 
    EmailVerificationRepository
)

from app.core.security import (
    generate_verification_token,  
    hash_verification_token
)

from app.core.exceptions import (
    InvalidTokenException, 
    TokenExpiredException
)

from app.config.settings import get_settings

setting = get_settings()


class EmailVerificationService:
    """Service quản lý xác thực email.
    
    Workflow:
    1. Sau khi đăng ký → tạo verification token → gửi email
    2. User click link → verify_email() → đánh dấu user đã xác thực
    
    Token được lưu dưới dạng hash để bảo mật.
    
    Attributes:
        user_repo: Repository để cập nhật trạng thái verified của user.
        verification_repo: Repository để quản lý verification tokens.
    """

    def __init__(self, user_repo: UserRepository, verification_repo: EmailVerificationRepository): 
        self.user_repo = user_repo
        self.verification_repo = verification_repo


    async def create_verification_token(self, user_id: UUID, email: str) -> str:
        """Tạo verification token mới cho user.
        
        Args:
            user_id: UUID của user cần xác thực email.
            email: Email của user.
            
        Returns:
            Plain token string (gửi trong email link).
            
        Note:
            Token được lưu trong DB dưới dạng hash.
            Plain token chỉ được trả về MỘT LẦN để gửi email.
        """
        plain_token, hashed_token = generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=setting.EMAIL_VERIFICATION_EXPIRE_MINUTES)
        
        


        await self.verification_repo.create(
            user_id=user_id, 
            token_hash=hashed_token, 
            email=email,
            expires_at=expires_at
        )

        return plain_token
    

    async def verify_email(self, token: str) -> bool:
        """Xác thực email bằng token từ link.
        
        Flow:
        1. Hash token đầu vào
        2. Tìm token record trong DB
        3. Kiểm tra chưa hết hạn
        4. Đánh dấu user là verified
        5. Đánh dấu token đã sử dụng
        
        Args:
            token: Plain token string từ email link.
            
        Returns:
            True nếu xác thực thành công.
            
        Raises:
            InvalidTokenException: Token không tồn tại hoặc đã sử dụng.
            TokenExpiredException: Token đã hết hạn.
        """
        hashed_token = hash_verification_token(token)
        verification_token = await self.verification_repo.get_by_token_hash(hashed_token)

        if not verification_token: 
            raise InvalidTokenException()
        
        if verification_token.expires_at < datetime.now(timezone.utc): 
            raise TokenExpiredException()
        
        await self.user_repo.verify_by_id(verification_token.user_id)
        await self.verification_repo.mark_verified(verification_token)

        return True 
        
    
    async def resend_email(self, user_id: UUID) -> str:
        """Gửi lại email xác thực.
        
        Xóa token cũ (nếu có) và tạo token mới.
        
        Args:
            user_id: UUID của user cần gửi lại.
            
        Returns:
            Plain token mới (để gửi trong email).
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
             # Should practically not happen if called correctly
             raise InvalidTokenException()

        await self.verification_repo.delete_by_user(user_id)
        return await self.create_verification_token(user_id, user.email)
    

    async def has_pending_verification(self, user_id: UUID) -> bool:
        """Kiểm tra user có verification pending không.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            True nếu có verification token chưa sử dụng.
        """
        token = await self.verification_repo.get_pending_by_user(user_id)
        return token is not None
        

def get_email_verification_service(
    user_repo: UserRepoDep, 
    verification_repo: EmailVerificationRepoDep
) -> EmailVerificationService:
    """Dependency injection factory cho EmailVerificationService."""
    return EmailVerificationService(user_repo, verification_repo)


EmailVerificationServiceDep = Annotated[EmailVerificationService, Depends(get_email_verification_service)]
