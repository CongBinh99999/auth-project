"""Chặn secret mẫu ngoài development, và dọn token hết hạn."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.config.database import AsyncSessionLocal
from app.config.settings import Settings
from app.core.security import hash_password
from app.main import purge_expired
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


def _settings(**kwargs) -> Settings:
    base = {"APP_ENV": "production", "JWT_SECRET": "x" * 40}
    return Settings(**{**base, **kwargs})


def test_development_tolerates_placeholder_secret():
    assert _settings(APP_ENV="development", JWT_SECRET="SECRET_KEY").APP_ENV == "development"


@pytest.mark.parametrize("secret", ["", "SECRET_KEY", "change_this_to_a_secure_random_string"])
def test_placeholder_secret_is_rejected_outside_development(secret):
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        _settings(JWT_SECRET=secret)


def test_short_secret_is_rejected_outside_development():
    with pytest.raises(RuntimeError, match="32"):
        _settings(JWT_SECRET="x" * 31)


def test_long_random_secret_is_accepted():
    assert len(_settings(JWT_SECRET="y" * 64).JWT_SECRET) == 64


def test_config_error_does_not_leak_other_settings():
    """Thông báo lỗi không được kèm SMTP_PASSWORD - lý do dùng RuntimeError."""
    with pytest.raises(RuntimeError) as exc:
        _settings(JWT_SECRET="SECRET_KEY", SMTP_PASSWORD="super-secret-value")

    assert "super-secret-value" not in str(exc.value)


async def test_purge_removes_expired_verification_token():
    async with AsyncSessionLocal() as session:
        role = await RoleRepository(session).get_default_role()
        user = await UserRepository(session).create(
            email=f"purge_{uuid4().hex[:8]}@example.com",
            hashed_password=hash_password("TestPassword123!"),
            full_name="Purge",
            role_id=role.id,
        )

        repo = EmailVerificationRepository(session)
        token = await repo.create(
            user_id=user.id,
            token_hash=f"expired-{uuid4().hex}",
            email=user.email,
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )
        token_hash = token.token_hash
        await session.commit()

    await purge_expired()

    async with AsyncSessionLocal() as session:
        assert await EmailVerificationRepository(session).get_by_token_hash(token_hash) is None
