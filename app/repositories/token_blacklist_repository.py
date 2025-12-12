# app/repositories/token_blacklist_repository.py
# 
# Purpose: Database access layer for Token Blacklist operations.
# 
# Implementation details:
# - class TokenBlacklistRepository:
#     def __init__(self, db: AsyncSession)
#     async def add(jti: str, expires_at: datetime) -> TokenBlacklist
#     async def is_blacklisted(jti: str) -> bool
#     async def cleanup_expired() -> int
