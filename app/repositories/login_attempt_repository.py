from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.login_attempt import LoginAttempt

# Đánh dấu bản ghi đăng ký trong bảng login_attempts.
REGISTER_MARKER = "register"


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


    async def count_failed_by_email(self, email: str, minutes: int = 15) -> int:
        """Đếm login thất bại gần đây của riêng một email."""
        return await self._count_failed(LoginAttempt.email == email, minutes)


    async def count_failed_by_ip(self, ip_address: str, minutes: int = 15) -> int:
        """Đếm login thất bại gần đây từ riêng một IP."""
        return await self._count_failed(LoginAttempt.ip_address == ip_address, minutes)


    async def _count_failed(self, criterion, minutes: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                and_(
                    criterion,
                    LoginAttempt.attempted_at >= cutoff,
                    LoginAttempt.is_successful.is_(False)
                )
            )
        )

        return result.scalar() or 0


    async def count_registrations_by_ip(self, ip_address: str, minutes: int) -> int:
        """Đếm số lần đăng ký gần đây từ một IP.

        Đăng ký được ghi vào chính bảng này với is_successful=True và
        failure_reason='register', nên không bao giờ lọt vào bộ đếm
        brute-force (bộ đó chỉ đếm is_successful=False).
        """
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(func.count())
            .select_from(LoginAttempt)
            .where(
                and_(
                    LoginAttempt.ip_address == ip_address,
                    LoginAttempt.failure_reason == REGISTER_MARKER,
                    LoginAttempt.attempted_at >= cutoff
                )
            )
        )

        return result.scalar() or 0


    async def is_blocked(
        self,
        email: str,
        ip_address: str,
        max_per_email: int = 5,
        max_per_ip: int = 20
    ) -> bool:
        """Kiểm tra email/IP có bị block không.

        Email và IP dùng ngưỡng RIÊNG. Gộp chung bằng OR ở một ngưỡng sẽ khiến
        năm lần gõ sai của một người khoá mọi tài khoản cùng đi qua một NAT,
        và sau reverse proxy thì khoá toàn bộ ứng dụng.
        """
        if await self.count_failed_by_email(email) >= max_per_email:
            return True

        return await self.count_failed_by_ip(ip_address) >= max_per_ip


    async def cleanup_old_attempts(self, days: int = 30) -> int: 
        """Xóa các login attempts cũ.
        
        Args:
            days: Số ngày giữ lại (default: 30).
            
        Returns:
            Số lượng records đã xóa.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        result = await self.db.execute(
            delete(LoginAttempt)
            .where(LoginAttempt.attempted_at <= cutoff)
        )

        return result.rowcount


    async def clear_failed_attempts(self, email: str, ip_address: str, minutes: int = 15) -> int:
        """Xóa failed attempts gần đây của email này sau khi login thành công.

        Chỉ xoá theo email: nếu xoá cả theo IP thì một tài khoản hợp lệ có thể
        reset bộ đếm IP và vô hiệu hoá ngưỡng IP.
        
        Args:
            email: Email của user.
            ip_address: IP address của user.
            minutes: Xóa attempts trong khoảng thời gian (default: 15).
            
        Returns:
            Số lượng records đã xóa.
        """
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        result = await self.db.execute(
            delete(LoginAttempt)
            .where(
                and_(
                    LoginAttempt.email == email,
                    LoginAttempt.attempted_at >= cutoff,
                    LoginAttempt.is_successful.is_(False)
                )
            )
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