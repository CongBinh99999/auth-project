from uuid import UUID
from typing import Optional, Annotated 
from datetime import datetime, timezone 
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession 
from fastapi import Depends

from app.config.database import get_db
from app.models.token_blacklist import TokenBlacklist


class TokenBlacklistRepository:
    """Repository cho TokenBlacklist entity - quản lý danh sách tokens bị vô hiệu hóa."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 


    async def create(self, **blacklist_data) -> TokenBlacklist: 
        """Thêm token vào blacklist.
        
        Args:
            **blacklist_data: Dữ liệu token (jti, token_type, user_id, expires_at, reason).
            
        Returns:
            TokenBlacklist đã được tạo.
        """
        token = TokenBlacklist(**blacklist_data)

        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)

        return token


    async def is_blacklisted(self, jti: str) -> bool:
        """Kiểm tra token có trong blacklist không.
        
        Args:
            jti: JWT ID của token.
            
        Returns:
            True nếu token bị blacklist, False nếu không.
        """
        result = await self.db.execute(
            select(TokenBlacklist)
            .where(TokenBlacklist.jti == jti)
        )

        return result.scalar_one_or_none() is not None


    async def cleanup_expired(self) -> int: 
        """Xóa các tokens đã hết hạn khỏi blacklist.
        
        Returns:
            Số lượng tokens đã xóa.
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            delete(TokenBlacklist)
            .where(TokenBlacklist.expires_at < now)
        )

        await self.db.flush()
        
        return result.rowcount


def get_token_blacklist_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenBlacklistRepository: 
    """Dependency để inject TokenBlacklistRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        TokenBlacklistRepository instance.
    """
    return TokenBlacklistRepository(db)


TokenBlacklistRepoDep = Annotated[TokenBlacklistRepository, Depends(get_token_blacklist_repository)]