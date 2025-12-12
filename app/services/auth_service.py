# app/services/auth_service.py
# 
# Purpose: High-level authentication business logic.
# 
# Implementation details:
# - class AuthService:
#     def __init__(self, db: AsyncSession)
#     async def register(register_data: RegisterRequest) -> UserResponse
#     async def authenticate_user(email: str, password: str) -> User
#     async def login(login_data: LoginRequest) -> TokenResponse
#     async def refresh_token(refresh_token: str) -> TokenResponse
#     async def logout(access_token: str, refresh_token: str | None) -> None
#     async def logout_all_sessions(user_id: str) -> int
