# app/services/token_family_service.py
# 
# Purpose: Token Family rotation logic.
# 
# Implementation details:
# - class TokenFamilyService:
#     def __init__(self, db: AsyncSession)
#     async def validate_refresh_token(refresh_token: str) -> tuple[TokenFamily, dict]
#     async def rotate_token(family: TokenFamily, user_id: str) -> str
#     async def revoke_family(family_id: str) -> None
#     async def revoke_all_user_sessions(user_id: str) -> int
