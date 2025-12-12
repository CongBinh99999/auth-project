# app/repositories/login_attempt_repository.py
# 
# Purpose: Database access layer for LoginAttempt operations.
# 
# Implementation details:
# - class LoginAttemptRepository:
#     def __init__(self, db: AsyncSession)
#     async def create(attempt_data) -> LoginAttempt
#     async def get_recent_by_email(email: str, minutes: int = 15) -> list[LoginAttempt]
#     async def get_recent_by_ip(ip_address: str, minutes: int = 15) -> list[LoginAttempt]
#     async def count_failed_attempts(email: str, ip_address: str, minutes: int = 15) -> int
#     async def is_blocked(email: str, ip_address: str, max_attempts: int = 5) -> bool
#     async def cleanup_old_attempts(days: int = 30) -> int
