from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.email_verification_token import EmailVerificationToken


class EmailVerificationRepository:
    """Repository cho EmailVerificationToken entity - quản lý tokens xác thực email."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 


    async def create(self, **email_verification_data) -> EmailVerificationToken:
        """Tạo email verification token mới.
        
        Args:
            **email_verification_data: Dữ liệu token (user_id, token_hash, expires_at).
            
        Returns:
            EmailVerificationToken đã được tạo.
        """
        email_verification = EmailVerificationToken(**email_verification_data)

        self.db.add(email_verification)
        await self.db.flush()
        await self.db.refresh(email_verification)

        return email_verification
    

    async def get_by_token_hash(self, token_hash: str) -> EmailVerificationToken | None:
        """Lấy token theo hash.
        
        Args:
            token_hash: Hash của token.
            
        Returns:
            EmailVerificationToken nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token_hash == token_hash)
        )

        return result.scalar_one_or_none()
    

    async def get_pending_by_user(self, user_id: UUID) -> EmailVerificationToken | None:
        """Lấy token pending của user (chưa verify, chưa hết hạn).
        
        Args:
            user_id: UUID của user.
            
        Returns:
            EmailVerificationToken nếu tìm thấy, None nếu không.
        """
        now = datetime.now(UTC)

        result = await self.db.execute(
            select(EmailVerificationToken)
            .where(
                and_(
                    EmailVerificationToken.user_id == user_id, 
                    EmailVerificationToken.verified_at.is_(None), 
                    EmailVerificationToken.expires_at > now
                )
            )
            .order_by(EmailVerificationToken.created_at.desc())
        )
        
        return result.scalar_one_or_none()


    async def mark_verified(self, token: EmailVerificationToken) -> EmailVerificationToken:
        """Đánh dấu token đã được xác thực.
        
        Args:
            token: EmailVerificationToken object cần đánh dấu.
            
        Returns:
            EmailVerificationToken đã được cập nhật.
        """
        token.verified_at = datetime.now(UTC)

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
            delete(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
        )

        return result.rowcount


    async def cleanup_expired(self) -> int:
        """Xóa các tokens đã hết hạn.
        
        Returns:
            Số lượng tokens đã xóa.
        """
        now = datetime.now(UTC)

        result = await self.db.execute(
            delete(EmailVerificationToken)
            .where(EmailVerificationToken.expires_at < now)
        )

        return result.rowcount


def get_email_verification_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> EmailVerificationRepository: 
    """Dependency để inject EmailVerificationRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        EmailVerificationRepository instance.
    """
    return EmailVerificationRepository(db)


EmailVerificationRepoDep = Annotated[EmailVerificationRepository, Depends(get_email_verification_repository)]
