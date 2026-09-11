import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.schemas.auth import TokenPayload

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

settings = get_settings()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
    jti: str | None = None 
) -> tuple[str, str, datetime]:
    """Create JWT token."""
    
    token_jti = jti if jti else str(uuid.uuid4())
    now = datetime.now(UTC)

    if expires_delta:
        expires_at = now + expires_delta
    elif token_type == "access":
        expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "jti": token_jti,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp())
    }
    
    if extra_claims:
        for key, value in extra_claims.items():
            if value is not None:
                payload[key] = str(value) if isinstance(value, uuid.UUID) else value

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token, token_jti, expires_at

def decode_token(token: str, expected_type: str | None = None) -> TokenPayload:
    """Decode JWT. Nếu truyền expected_type, token sai loại sẽ bị từ chối."""
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    payload = TokenPayload(**data)

    if expected_type is not None and payload.type != expected_type:
        raise JWTError(f"Expected {expected_type} token, got {payload.type}")

    return payload

def generate_verification_token() -> tuple[str, str]:
    plain_token = str(uuid.uuid4())
    hashed_token = hash_verification_token(plain_token)
    return plain_token, hashed_token

def verify_verification_token(plain_token: str, hashed_token: str) -> bool:
    return hash_verification_token(plain_token) == hashed_token    

def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()