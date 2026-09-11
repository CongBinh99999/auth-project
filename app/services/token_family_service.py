"""Token Family Service - Refresh token rotation management.

Quản lý Token Families để implement Refresh Token Rotation,
bảo vệ chống token theft attacks.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from jose import JWTError
from pydantic import ValidationError

from app.config.settings import get_settings
from app.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
)
from app.core.security import decode_token
from app.models.token_family import TokenFamily
from app.repositories.token_family_repository import (
    TokenFamilyRepoDep,
    TokenFamilyRepository,
)
from app.schemas.auth import TokenPayload
from app.utils.constants import TokenType

setting = get_settings()


class TokenFamilyService:
    """Service quản lý Token Families cho refresh token rotation.
    
    Refresh Token Rotation:
    - Mỗi lần refresh → tạo refresh token MỚI và vô hiệu hóa token cũ
    - Nếu token cũ được sử dụng → revoke toàn bộ family (token theft detection)
    
    Cung cấp các chức năng:
    - Tạo token family mới khi login
    - Validate refresh token với theft detection
    - Rotate tokens
    - Revoke sessions
    
    Attributes:
        token_family_repo: Repository để thao tác với TokenFamily entity.
    """

    def __init__(self, token_family_repo: TokenFamilyRepository):
        self.token_family_repo = token_family_repo


    async def create_family(self, user_id: UUID, initial_jti: str, device_id: UUID | None = None) -> TokenFamily:
        """Tạo token family mới khi user login.
        
        Args:
            user_id: UUID của user.
            initial_jti: JTI của refresh token đầu tiên.
            device_id: UUID của device (optional).
            
        Returns:
            TokenFamily entity mới.
        """
        expires_at = datetime.now(UTC) + timedelta(days=setting.REFRESH_TOKEN_EXPIRE_DAYS)

        return await self.token_family_repo.create(
            user_id=user_id,
            device_id=device_id,
            current_jti=initial_jti,
            expires_at=expires_at
        )
    

    async def validate_refresh_token(self, refresh_token: str) -> tuple[TokenFamily, TokenPayload]:
        """Validate refresh token và phát hiện token theft.
        
        Flow:
        1. Decode refresh token
        2. Kiểm tra có family_id không
        3. Kiểm tra hết hạn
        4. Lấy family từ DB
        5. TOKEN THEFT DETECTION: Nếu jti != current_jti → revoke toàn bộ family
        
        Args:
            refresh_token: Refresh token string cần validate.
            
        Returns:
            Tuple (TokenFamily, TokenPayload).
            
        Raises:
            InvalidTokenException: Token không hợp lệ hoặc family không tồn tại.
            TokenExpiredException: Token đã hết hạn.
            TokenRevokedException: Phát hiện token theft, đã revoke toàn bộ sessions.
        """
        try:
            payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        except (JWTError, ValidationError) as e:
            raise InvalidTokenException() from e
        
        if not payload.family_id: 
            raise InvalidTokenException()
        
        if payload.is_expired: 
            raise TokenExpiredException()

        family = await self.token_family_repo.get_by_id(payload.family_id)

        if not family: 
            raise InvalidTokenException()
        
        # Token theft detection
        if family.current_jti != str(payload.jti):
            await self.token_family_repo.revoke_all_for_user(family.user_id)
            raise TokenRevokedException() 

        return family, payload

    
    async def rotate_token(self, family: TokenFamily, new_jti: str) -> TokenFamily:
        """Rotate refresh token - cập nhật current_jti mới.
        
        Gọi sau khi tạo refresh token mới trong quá trình refresh.
        
        Args:
            family: TokenFamily entity cần rotate.
            new_jti: JTI của refresh token mới.
            
        Returns:
            TokenFamily đã cập nhật.
        """
        return await self.token_family_repo.update_token(family, new_jti=new_jti)

    
    async def revoke_family(self, family_id: UUID) -> TokenFamily | None:
        """Revoke một token family (logout session đó).
        
        Args:
            family_id: UUID của family cần revoke.
            
        Returns:
            TokenFamily đã revoke.
            
        Raises:
            InvalidTokenException: Family không tồn tại.
        """
        family = await self.token_family_repo.get_by_id(family_id)
        if not family: 
            raise InvalidTokenException()
        return await self.token_family_repo.revoke(family)


    async def revoke_all_user_sessions(self, user_id: UUID) -> int:
        """Revoke tất cả sessions của user (logout all devices).
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng families đã revoke.
        """
        return await self.token_family_repo.revoke_all_for_user(user_id)
        

    async def get_family_by_id(self, family_id: UUID) -> TokenFamily | None:
        """Lấy token family theo ID.
        
        Args:
            family_id: UUID của family.
            
        Returns:
            TokenFamily hoặc None nếu không tìm thấy.
        """
        return await self.token_family_repo.get_by_id(family_id)


    async def get_family_by_jti(self, jti: str) -> TokenFamily | None:
        """Lấy token family theo JTI của refresh token.
        
        Args:
            jti: JWT ID của refresh token.
            
        Returns:
            TokenFamily hoặc None nếu không tìm thấy.
        """
        return await self.token_family_repo.get_by_jti(jti)


    async def update_current_jti(self, family_id: UUID, new_jti: str) -> TokenFamily:
        """Update current JTI của token family.
        
        Args:
            family_id: UUID của token family
            new_jti: JTI mới
            
        Returns:
            TokenFamily đã cập nhật
        """
        family = await self.token_family_repo.get_by_id(family_id)
        if not family:
            raise InvalidTokenException("Token family not found")
        
        return await self.token_family_repo.update_token(family, new_jti=new_jti)


    async def update_last_used(self, family: TokenFamily) -> TokenFamily:
        """Cập nhật last_used_at của token family.
        
        Args:
            family: TokenFamily entity cần cập nhật.
            
        Returns:
            TokenFamily đã cập nhật.
        """
        return await self.token_family_repo.update_token(
            family, 
            last_used_at=datetime.now(UTC)
        )


def get_token_family_service(
    token_family_repo: TokenFamilyRepoDep
) -> TokenFamilyService:
    """Dependency injection factory cho TokenFamilyService."""
    return TokenFamilyService(token_family_repo)


TokenFamilyServiceDep = Annotated[TokenFamilyService, Depends(get_token_family_service)]
