# app/core/dependencies.py
# 
# Purpose: FastAPI Dependencies.
# 
# Implementation details:
# - oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
# - Function get_current_user(token, db) -> User
# - Function get_current_active_user(user) -> User
# - Type aliases: CurrentUser, ActiveUser, DbSession
