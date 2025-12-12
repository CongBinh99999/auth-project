# app/core/security.py
# 
# Purpose: Cryptographic utilities.
# 
# Implementation details:
# - pwd_context = CryptContext(schemes=["bcrypt"])
# - Function verify_password(plain, hashed) -> bool
# - Function get_password_hash(password) -> str
# - Function create_access_token(user_id, expires_delta) -> tuple[str, str]
# - Function create_refresh_token(user_id, family_id, expires_delta) -> tuple[str, str]
# - Function decode_token(token) -> dict | None
# - Function verify_token(token, token_type) -> dict | None
