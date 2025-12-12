# app/repositories/password_reset_repository.py
# 
# Purpose: Database access layer for PasswordResetToken operations.
# 
# Implementation details:
# - class PasswordResetRepository:
#     def __init__(self, db: AsyncSession)
#     async def create(user_id: UUID, token_hash: str, expires_at: datetime) -> PasswordResetToken
#     async def get_by_token_hash(token_hash: str) -> PasswordResetToken | None
#     async def get_pending_by_user(user_id: UUID) -> PasswordResetToken | None
#     async def mark_used(token: PasswordResetToken) -> PasswordResetToken
#     async def delete_by_user(user_id: UUID) -> int
#     async def cleanup_expired() -> int
