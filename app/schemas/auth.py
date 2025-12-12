# app/schemas/auth.py
# 
# Purpose: Pydantic schemas for Authentication payloads.
# 
# Implementation details:
# - LoginRequest: email, password
# - TokenResponse: access_token, refresh_token, token_type
# - RefreshTokenRequest: refresh_token
# - RegisterRequest: Inherits from UserCreate
# - TokenPayload: sub, jti, type, family_id, exp
