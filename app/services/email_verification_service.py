# app/services/email_verification_service.py
# 
# Purpose: Email verification business logic.
# 
# Implementation details:
# - class EmailVerificationService:
#     def __init__(self, db: AsyncSession)
#     async def create_verification_token(user_id: UUID, email: str) -> str
#     async def verify_email(token: str) -> bool
#     async def resend_verification(user_id: UUID) -> str
#     async def is_email_verified(user_id: UUID) -> bool
#     async def generate_token() -> str
#     async def hash_token(token: str) -> str
