from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.token_family import TokenFamily


class TokenFamilyRepository:
    """Repository cho TokenFamily entity - quản lý Refresh Token Rotation."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 

    
    async def create(self, **token_family_data) -> TokenFamily:
        """Tạo token family mới.
        
        Args:
            **token_family_data: Dữ liệu token family (user_id, current_jti, expires_at, ...).
            
        Returns:
            TokenFamily đã được tạo.
        """
        token_family = TokenFamily(**token_family_data)

        self.db.add(token_family)
        await self.db.flush()
        await self.db.refresh(token_family)

        return token_family 


    async def get_by_id(self, family_id: UUID) -> TokenFamily | None: 
        """Lấy token family theo ID.
        
        Args:
            family_id: UUID của token family.
            
        Returns:
            TokenFamily nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(TokenFamily)
            .where(TokenFamily.id == family_id)
        )

        return result.scalar_one_or_none()


    async def get_by_jti(self, jti: str) -> TokenFamily | None: 
        """Lấy token family theo JTI (JWT ID).
        
        Args:
            jti: JWT ID của token.
            
        Returns:
            TokenFamily nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(TokenFamily)
            .where(TokenFamily.current_jti == jti)
        )

        return result.scalar_one_or_none()


    async def update_token(self, token_family: TokenFamily, **update_data) -> TokenFamily:
        """Cập nhật thông tin token family.
        
        Args:
            token_family: TokenFamily object cần cập nhật.
            **update_data: Dữ liệu cần cập nhật (current_jti, last_used_at, ...).
            
        Returns:
            TokenFamily đã được cập nhật.
        """
        for key, value in update_data.items(): 
            if hasattr(token_family, key): 
                setattr(token_family, key, value)
        
        await self.db.flush()
        await self.db.refresh(token_family)

        return token_family


    async def revoke(self, family: TokenFamily) -> TokenFamily:
        """Thu hồi (revoke) token family.
        
        Args:
            family: TokenFamily object cần revoke.
            
        Returns:
            TokenFamily đã được revoke.
        """
        family.is_revoked = True

        await self.db.flush()
        await self.db.refresh(family)

        return family


    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Thu hồi tất cả token families của một user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng token families đã revoke.
        """
        result = await self.db.execute(
            update(TokenFamily)
            .where(TokenFamily.user_id == user_id)
            .values(is_revoked=True)
        )
        
        return result.rowcount


    async def revoke_all_for_device(self, device_id: UUID) -> int:
        """Thu hồi mọi token family gắn với một device.

        Chặn device mà không gọi hàm này thì phiên đang chạy trên device đó
        vẫn refresh được vô hạn - đúng tình huống điện thoại bị mất.
        """
        result = await self.db.execute(
            update(TokenFamily)
            .where(TokenFamily.device_id == device_id)
            .values(is_revoked=True)
        )

        return result.rowcount


    async def is_valid_family(self, family: TokenFamily) -> bool:
        """Kiểm tra token family có hợp lệ không.
        
        Token family hợp lệ khi chưa hết hạn và chưa bị revoke.
        
        Args:
            family: TokenFamily object cần kiểm tra.
            
        Returns:
            True nếu hợp lệ, False nếu không.
        """
        now = datetime.now(UTC)
        return family.expires_at > now and not family.is_revoked 



def get_token_family_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenFamilyRepository: 
    """Dependency để inject TokenFamilyRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        TokenFamilyRepository instance.
    """
    return TokenFamilyRepository(db)


TokenFamilyRepoDep = Annotated[TokenFamilyRepository, Depends(get_token_family_repository)]
