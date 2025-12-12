# app/controllers/auth_controller.py
# 
# Purpose: Controller for authentication operations.
# 
# Implementation details:
# - class AuthController:
#     def __init__(self, db: AsyncSession)
#     async def register(request: RegisterRequest) -> UserResponse
#     async def login(request: LoginRequest) -> TokenResponse
#     async def refresh(request: RefreshTokenRequest) -> TokenResponse
#     async def logout(access_token: str, refresh_token: str | None) -> dict
#     async def logout_all(user_id: str) -> dict
