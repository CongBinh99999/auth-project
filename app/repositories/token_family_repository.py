# app/repositories/token_family_repository.py
# 
# Purpose: Database access layer for Token Family operations.
# 
# Implementation details:
# - class TokenFamilyRepository:
#     def __init__(self, db: AsyncSession)
#     async def create(user_id: str, refresh_token_jti: str, expires_at: datetime) -> TokenFamily
#     async def get_by_id(family_id: str) -> TokenFamily | None
#     async def get_by_jti(jti: str) -> TokenFamily | None
#     async def update_token(family: TokenFamily, new_jti: str) -> TokenFamily
#     async def revoke(family: TokenFamily) -> TokenFamily
#     async def revoke_all_for_user(user_id: str) -> int
#     async def is_valid_family(family_id: str, jti: str) -> bool
