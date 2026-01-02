from datetime import datetime, timezone
from uuid import UUID 
from typing import Annotated, Optional 
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends 

from app.config.database import get_db
from app.models.password_reset_token import PasswordResetToken


class PasswordResetRepository:
    """Repository cho PasswordResetToken entity - quản lý tokens đặt lại mật khẩu."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 


    async def create(self, **password_reset_data) -> PasswordResetToken: 
        """Tạo password reset token mới.
        
        Args:
            **password_reset_data: Dữ liệu token (user_id, token_hash, expires_at).
            
        Returns:
            PasswordResetToken đã được tạo.
        """
        password_reset = PasswordResetToken(**password_reset_data)

        self.db.add(password_reset)
        await self.db.flush()
        await self.db.refresh(password_reset)

        return password_reset


    async def get_by_token_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Lấy token theo hash.
        
        Args:
            token_hash: Hash của token.
            
        Returns:
            PasswordResetToken nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.token_hash == token_hash)
        )

        return result.scalar_one_or_none()


    async def get_pending_by_user(self, user_id: UUID) -> Optional[PasswordResetToken]:
        """Lấy token pending của user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            PasswordResetToken nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
        )

        return result.scalar_one_or_none()


    async def mark_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """Đánh dấu token đã được sử dụng.
        
        Args:
            token: PasswordResetToken object cần đánh dấu.
            
        Returns:
            PasswordResetToken đã được cập nhật.
        """
        token.used_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(token)

        return token


    async def delete_by_user(self, user_id: UUID) -> int:
        """Xóa tất cả tokens của một user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng tokens đã xóa.
        """
        result = await self.db.execute(
            delete(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
        )

        return result.rowcount


    async def cleanup_expired(self) -> int:
        """Xóa các tokens đã hết hạn.
        
        Returns:
            Số lượng tokens đã xóa.
        """
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            delete(PasswordResetToken)
            .where(PasswordResetToken.expires_at < now)
        )

        return result.rowcount


def get_password_reset_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PasswordResetRepository: 
    """Dependency để inject PasswordResetRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        PasswordResetRepository instance.
    """
    return PasswordResetRepository(db)


PasswordResetRepoDep = Annotated[PasswordResetRepository, Depends(get_password_reset_repository)]