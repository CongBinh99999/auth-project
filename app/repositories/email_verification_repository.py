# app/repositories/email_verification_repository.py
# 
# Purpose: Database access layer for EmailVerificationToken operations.
# 
# Implementation details:
# - class EmailVerificationRepository:
#     def __init__(self, db: AsyncSession)
#     async def create(user_id: UUID, email: str, token_hash: str, expires_at: datetime) -> EmailVerificationToken
#     async def get_by_token_hash(token_hash: str) -> EmailVerificationToken | None
#     async def get_pending_by_user(user_id: UUID) -> EmailVerificationToken | None
#     async def mark_verified(token: EmailVerificationToken) -> EmailVerificationToken
#     async def delete_by_user(user_id: UUID) -> int
#     async def cleanup_expired() -> int
