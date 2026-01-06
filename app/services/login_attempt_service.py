"""Login Attempt Service - Rate limiting and brute-force protection.

Theo dõi và kiểm soát các lần đăng nhập để bảo vệ
chống brute-force attacks.
"""

from uuid import UUID 
from typing import Annotated 
from fastapi import Depends

from app.repositories.login_attempt_repository import (
    LoginAttemptRepository, 
    LoginAttemptRepoDep
)

from app.models.login_attempt import LoginAttempt


class LoginAttemptService:
    """Service quản lý rate limiting cho login.
    
    Cung cấp các chức năng:
    - Kiểm tra user/IP có bị block không
    - Đếm số lần login thất bại
    - Ghi nhận login attempts
    - Xóa attempts sau khi login thành công
    
    Constants:
        MAX_ATTEMPTS: Số lần thất bại tối đa trước khi bị block (default: 5).
        BLOCK_DURATION_MINUTES: Thời gian block (default: 15 phút).
        
    Attributes:
        login_attempt_repo: Repository để thao tác với LoginAttempt entity.
    """

    def __init__(self, login_attempt_repo: LoginAttemptRepository): 
        self.login_attempt_repo = login_attempt_repo 
    

    MAX_ATTEMPTS: int = 5
    BLOCK_DURATION_MINUTES: int = 15


    async def is_blocked(self, email: str, ip_address: str) -> bool:
        """Kiểm tra email hoặc IP có bị block không.
        
        Args:
            email: Email cần kiểm tra.
            ip_address: IP address cần kiểm tra.
            
        Returns:
            True nếu bị block (vượt quá MAX_ATTEMPTS).
        """
        return await self.login_attempt_repo.is_blocked(
            email, 
            ip_address, 
            max_attempts=self.MAX_ATTEMPTS
        )


    async def get_failed_attempts_count(self, email: str, ip_address: str) -> int:
        """Đếm số lần login thất bại gần đây.
        
        Args:
            email: Email cần kiểm tra.
            ip_address: IP address cần kiểm tra.
            
        Returns:
            Số lần thất bại trong BLOCK_DURATION_MINUTES phút gần đây.
        """
        return await self.login_attempt_repo.count_failed_attempts(
            email, 
            ip_address, 
            minutes=self.BLOCK_DURATION_MINUTES
        )


    async def get_remaining_attempts(self, email: str, ip_address: str) -> int:
        """Tính số lần thử còn lại trước khi bị block.
        
        Args:
            email: Email cần kiểm tra.
            ip_address: IP address cần kiểm tra.
            
        Returns:
            Số lần thử còn lại (≥ 0).
        """
        failing = await self.get_failed_attempts_count(email, ip_address)
        return max(0, self.MAX_ATTEMPTS - failing)


    async def cleanup_old_attempts(self, days: int = 30) -> int:
        """Xóa các login attempts cũ để maintain database.
        
        Args:
            days: Xóa attempts cũ hơn số ngày này (default: 30).
            
        Returns:
            Số lượng records đã xóa.
        """
        return await self.login_attempt_repo.cleanup_old_attempts(days)


    async def record_attempt(
        self,
        email: str,
        ip_address: str,
        is_successful: bool,
        user_id: UUID | None = None,
        user_agent: str | None = None,
        failure_reason: str | None = None
    ) -> LoginAttempt:
        """Ghi nhận một login attempt.
        
        Args:
            email: Email đang login.
            ip_address: IP address của request.
            is_successful: True nếu login thành công.
            user_id: UUID của user (nếu có).
            user_agent: User agent string của browser.
            failure_reason: Lý do thất bại (nếu có).
            
        Returns:
            LoginAttempt entity đã tạo.
        """
        return await self.login_attempt_repo.create(
            email=email,
            ip_address=ip_address,
            is_successful=is_successful,
            user_id=user_id,
            user_agent=user_agent,
            failure_reason=failure_reason
        )


    async def clear_attempts_on_success(self, email: str, ip_address: str) -> int:
        """Xóa các failed attempts sau khi login thành công.
        
        Gọi method này sau khi user đăng nhập thành công để reset counter,
        cho phép user bắt đầu lại với số lần thử đầy đủ.
        
        Args:
            email: Email của user vừa login thành công.
            ip_address: IP address của user.
            
        Returns:
            Số lượng failed attempts đã xóa.
        """
        return await self.login_attempt_repo.clear_failed_attempts(
            email, 
            ip_address, 
            minutes=self.BLOCK_DURATION_MINUTES
        ) 


def get_login_attempt_service(
    attempt_repo: LoginAttemptRepoDep 
) -> LoginAttemptService:
    """Dependency injection factory cho LoginAttemptService."""
    return LoginAttemptService(attempt_repo)


LoginAttemptServiceDep = Annotated[LoginAttemptService, Depends(get_login_attempt_service)]