# app/api/v1/auth.py
# 
# Purpose: Auth endpoints (Router layer).
# 
# Implementation details:
# - router = APIRouter(prefix="/auth", tags=["Authentication"])
# - POST /register -> AuthController.register
# - POST /login -> AuthController.login (OAuth2PasswordRequestForm)
# - POST /refresh -> AuthController.refresh
# - POST /logout -> AuthController.logout
# - POST /logout-all -> AuthController.logout_all
# - Dependencies: DbSession, ActiveUser, oauth2_scheme
