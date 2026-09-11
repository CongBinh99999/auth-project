from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

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


    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
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


    async def get_pending_by_user(self, user_id: UUID) -> PasswordResetToken | None:
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


    async def mark_used_if_unused(self, token_hash: str) -> tuple[UUID, datetime] | None:
        """Đánh dấu token đã dùng, chỉ khi nó còn chưa dùng.

        UPDATE có điều kiện nên hai request song song cùng token chỉ một cái
        thắng - cái còn lại nhận None.

        Returns:
            (user_id, expires_at) nếu giành được token, None nếu không.
        """
        result = await self.db.execute(
            update(PasswordResetToken)
            .where(
                and_(
                    PasswordResetToken.token_hash == token_hash,
                    PasswordResetToken.used_at.is_(None),
                )
            )
            .values(used_at=datetime.now(UTC))
            .returning(
                PasswordResetToken.user_id,
                PasswordResetToken.expires_at,
            )
        )

        return result.one_or_none()


    async def mark_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """Đánh dấu token đã được sử dụng.
        
        Args:
            token: PasswordResetToken object cần đánh dấu.
            
        Returns:
            PasswordResetToken đã được cập nhật.
        """
        token.used_at = datetime.now(UTC)

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
        now = datetime.now(UTC)

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