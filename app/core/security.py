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
from app.schemas.auth import TokenPayload
import uuid
from passlib.context import CryptContext 
from jose import jwt
from datetime import datetime, timedelta, timezone 
from app.config.settings import get_settings
from typing import Optional, Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str: 
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool: 
    return pwd_context.verify(plain_password, hashed_password) 


settings = get_settings()

def create_token (
    subject: str,
    token_type: str, 
    expires_delta: Optional[timedelta] = None, 
    extra_claims: Optional[dict[str, Any]] = None
) -> tuple[str, str, datetime]: 
    """
    Create JWT token.
    
    Returns:
        tuple: (token, jti, expires_at)
    """
    jti = uuid.uuid4()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expires_at = now + expires_delta
    elif token_type == "access":
        expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = TokenPayload(
        sub=uuid.UUID(subject),
        jti=jti,
        type=token_type,
        family_id=extra_claims.get("family_id") if extra_claims else None,
        iat=now,
        exp=expires_at
    )

    token = jwt.encode(payload.model_dump(mode="json"), settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return token, str(jti), expires_at

def create_access_token(
    subject:str, 
    extra_claims: Optional[dict[str, Any]] = None
) -> tuple[str, str, datetime]:
    return create_token(subject, "access", extra_claims=extra_claims)

def create_refresh_token(
    subject:str, 
    extra_claims: Optional[dict[str, Any]] = None
) -> tuple[str, str, datetime]:
    return create_token(subject, "refresh", extra_claims=extra_claims)

def decode_token(
    token: str
) -> TokenPayload: 
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return TokenPayload(**data)

def generate_verification_token() -> tuple[str, str]: 
    plain_token = str(uuid.uuid4())
    hashed_token = hash_password(plain_token)
    return plain_token, hashed_token

def verify_verification_token(plain_token: str, hashed_token: str) -> bool: 
    return verify_password(plain_token, hashed_token)    