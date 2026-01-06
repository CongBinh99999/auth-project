"""Token Service - JWT token management.

Quản lý JWT tokens bao gồm tạo, verify, và blacklist tokens.
"""

from uuid import UUID 
from typing import Annotated
from fastapi import Depends
from datetime import datetime

from app.repositories.token_blacklist_repository import (
    TokenBlacklistRepository, 
    TokenBlacklistRepoDep
)

from app.schemas.auth import (
    TokenPayload,
    TokenResponse
)

from app.models.token_blacklist import TokenBlacklist, TokenType

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token
)

from app.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException
)

from app.config.settings import get_settings

setting = get_settings()


class TokenService:
    """Service quản lý JWT tokens.
    
    Cung cấp các chức năng:
    - Tạo access token và refresh token
    - Verify và decode token
    - Blacklist tokens (cho logout)
    
    Attributes:
        blacklist_repo: Repository để quản lý token blacklist.
    """

    def __init__(self, blacklist_repo: TokenBlacklistRepository):
        self.blacklist_repo = blacklist_repo


    def create_access_token(self, user_id: UUID, family_id: UUID | None = None) -> tuple[str, str, datetime]:
        """Tạo access token mới.
        
        Args:
            user_id: UUID của user.
            family_id: UUID của token family (optional).
            
        Returns:
            Tuple (token_string, jti, expires_at).
        """
        extra_claims = {"family_id": family_id} if family_id is not None else None

        return create_access_token(
            subject=str(user_id), 
            extra_claims=extra_claims
        )


    def create_refresh_token(self, user_id: UUID, family_id: UUID) -> tuple[str, str, datetime]:
        """Tạo refresh token mới.
        
        Args:
            user_id: UUID của user.
            family_id: UUID của token family (bắt buộc).
            
        Returns:
            Tuple (token_string, jti, expires_at).
        """
        extra_claims = {"family_id": family_id}

        return create_refresh_token(
            subject=str(user_id),
            extra_claims=extra_claims
        )


    def create_pair_token(self, user_id: UUID, family_id: UUID) -> TokenResponse:
        """Tạo cặp access + refresh tokens.
        
        Args:
            user_id: UUID của user.
            family_id: UUID của token family.
            
        Returns:
            TokenResponse chứa cả access và refresh tokens.
        """
        access_token, access_jti, access_exp = self.create_access_token(
            user_id=user_id,
            family_id=family_id
        )

        refresh_token, refresh_jti, refresh_exp = self.create_refresh_token(
            user_id=user_id,
            family_id=family_id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token, 
            token_type="bearer",
            expires_in=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )


    def decode_token(self, token: str) -> TokenPayload:
        """Decode JWT token thành payload.
        
        Args:
            token: JWT token string cần decode.
            
        Returns:
            TokenPayload chứa thông tin từ token.
            
        Raises:
            InvalidTokenException: Token không hợp lệ hoặc không decode được.
        """
        try:
            return decode_token(token)
        except Exception:
            raise InvalidTokenException()


    async def verify_token(self, token: str) -> TokenPayload:
        """Verify token hợp lệ và chưa bị blacklist.
        
        Args:
            token: JWT token string cần verify.
            
        Returns:
            TokenPayload nếu token hợp lệ.
            
        Raises:
            InvalidTokenException: Token không hợp lệ hoặc bị blacklist.
            TokenExpiredException: Token đã hết hạn.
        """
        payload = self.decode_token(token)

        if payload.is_expired: 
            raise TokenExpiredException()
        
        if await self.is_blacklisted(str(payload.jti)):
            raise InvalidTokenException() 

        return payload

    
    async def is_blacklisted(self, jti: str) -> bool:
        """Kiểm tra token có trong blacklist không.
        
        Args:
            jti: JWT ID của token.
            
        Returns:
            True nếu token bị blacklist.
        """
        return await self.blacklist_repo.is_blacklisted(jti)
     
     
    async def blacklist_token(
        self,
        jti: str,
        token_type: TokenType,
        user_id: UUID,
        expires_at: datetime,
        reason: str = "logout"
    ) -> TokenBlacklist:
        """Thêm token vào blacklist.
        
        Args:
            jti: JWT ID của token.
            token_type: Loại token (ACCESS hoặc REFRESH).
            user_id: UUID của user sở hữu token.
            expires_at: Thời điểm token hết hạn.
            reason: Lý do blacklist (default: "logout").
            
        Returns:
            TokenBlacklist entity đã tạo.
        """
        return await self.blacklist_repo.create(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason
        )


def get_token_blacklist_service(
    blacklist_repo: TokenBlacklistRepoDep
) -> TokenService:
    """Dependency injection factory cho TokenService."""
    return TokenService(blacklist_repo)


TokenBlacklistServiceDep = Annotated[TokenService, Depends(get_token_blacklist_service)]