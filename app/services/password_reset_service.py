# app/services/password_reset_service.py
# 
# Purpose: Password reset business logic.
# 
# Implementation details:
# - class PasswordResetService:
#     def __init__(self, db: AsyncSession)
#     async def request_reset(email: str) -> str | None
#     async def validate_token(token: str) -> PasswordResetToken | None
#     async def reset_password(token: str, new_password: str) -> bool
#     async def generate_token() -> str
#     async def hash_token(token: str) -> str
