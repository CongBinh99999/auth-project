from uuid import UUID 
from typing import List, Optional, Annotated 
from sqlalchemy import select, update, and_, func, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession 
from fastapi import Depends
from datetime import datetime, timezone, timedelta

from app.config.database import get_db
from app.models.login_attempt import LoginAttempt


class LoginAttemptRepository: 
    """Repository cho LoginAttempt entity - theo dõi và quản lý các lần đăng nhập."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 


    async def create(self, **attempt_data) -> LoginAttempt: 
        """Tạo login attempt mới.
        
        Args:
            **attempt_data: Dữ liệu attempt (email, ip_address, is_successful, ...).
            
        Returns:
            LoginAttempt đã được tạo.
        """
        attempt = LoginAttempt(**attempt_data)

        self.db.add(attempt)
        await self.db.flush()
        await self.db.refresh(attempt)

        return attempt


    async def get_recent_by_email(self, email: str, minutes: int = 15) -> list[LoginAttempt]: 
        """Lấy các login attempts gần đây theo email.
        
        Args:
            email: Email cần tìm.
            minutes: Số phút gần đây (default: 15).
            
        Returns:
            Danh sách LoginAttempt trong khoảng thời gian.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(LoginAttempt)
            .where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.attempted_at >= cutoff
                )
            )
        )

        return list(result.scalars().all())


    async def get_recent_by_ip(self, ip_address: str, minutes: int = 15) -> list[LoginAttempt]: 
        """Lấy các login attempts gần đây theo IP.
        
        Args:
            ip_address: IP address cần tìm.
            minutes: Số phút gần đây (default: 15).
            
        Returns:
            Danh sách LoginAttempt trong khoảng thời gian.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(LoginAttempt)
            .where(
                and_(
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.attempted_at >= cutoff
                )
            )
        )

        return list(result.scalars().all())


    async def count_failed_attempts(self, email: str, ip_address: str, minutes: int = 15) -> int: 
        """Đếm số lần login thất bại theo email hoặc IP.
        
        Args:
            email: Email cần kiểm tra.
            ip_address: IP address cần kiểm tra.
            minutes: Số phút gần đây (default: 15).
            
        Returns:
            Số lần login thất bại.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                and_(
                    or_(
                        LoginAttempt.email == email,
                        LoginAttempt.ip_address == ip_address
                    ),
                    LoginAttempt.attempted_at >= cutoff,
                    LoginAttempt.is_successful == False
                )
            )
        )

        return result.scalar() or 0


    async def is_blocked(self, email: str, ip_address: str, max_attempts: int = 5) -> bool: 
        """Kiểm tra email/IP có bị block không.
        
        Args:
            email: Email cần kiểm tra.
            ip_address: IP address cần kiểm tra.
            max_attempts: Số lần thất bại tối đa (default: 5).
            
        Returns:
            True nếu bị block, False nếu không.
        """
        failed_count = await self.count_failed_attempts(email, ip_address)
        return failed_count >= max_attempts


    async def cleanup_old_attempts(self, days: int = 30) -> int: 
        """Xóa các login attempts cũ.
        
        Args:
            days: Số ngày giữ lại (default: 30).
            
        Returns:
            Số lượng records đã xóa.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            delete(LoginAttempt)
            .where(LoginAttempt.attempted_at <= cutoff)
        )

        return result.rowcount


def get_login_attempt_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> LoginAttemptRepository: 
    """Dependency để inject LoginAttemptRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        LoginAttemptRepository instance.
    """
    return LoginAttemptRepository(db)


LoginAttemptRepoDep = Annotated[LoginAttemptRepository, Depends(get_login_attempt_repository)]