"""Email verification - token dùng một lần, resend không lộ email tồn tại."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import (
    EmailSendFailedException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.core.security import hash_verification_token
from app.services.auth_service import AuthService
from app.services.email_verification_service import EmailVerificationService


class _UserRepo:
    def __init__(self, user=None):
        self.user = user
        self.verified = []

    async def get_by_email(self, email):
        return self.user

    async def get_by_id(self, user_id):
        return self.user

    async def verify_by_id(self, user_id):
        self.verified.append(user_id)


class _VerificationRepo:
    def __init__(self, token=None):
        self.token = token
        self.marked = []

    async def get_by_token_hash(self, token_hash):
        return self.token

    async def mark_verified(self, token):
        token.verified_at = datetime.now(UTC)
        self.marked.append(token)


class _VerificationService:
    def __init__(self):
        self.calls = []

    async def resend_email(self, user_id):
        self.calls.append(user_id)
        return "plain-token"


class _EmailService:
    def __init__(self, ok=True):
        self.ok = ok
        self.sent = []

    def send_verification_email(self, to_email, token):
        self.sent.append(to_email)
        return self.ok


def _token(plain: str, *, verified_at=None, expires_in=timedelta(minutes=15)):
    return SimpleNamespace(
        user_id=uuid4(),
        token_hash=hash_verification_token(plain),
        verified_at=verified_at,
        expires_at=datetime.now(UTC) + expires_in,
    )


def _auth_service(user, verification, email):
    return AuthService(_UserRepo(user), None, None, None, None, verification, email)


async def test_verify_email_accepts_fresh_token():
    repo = _VerificationRepo(_token("abc"))
    users = _UserRepo()
    service = EmailVerificationService(users, repo)

    assert await service.verify_email("abc") is True
    assert repo.marked


async def test_verify_email_rejects_used_token():
    repo = _VerificationRepo(_token("abc", verified_at=datetime.now(UTC)))
    service = EmailVerificationService(_UserRepo(), repo)

    with pytest.raises(InvalidTokenException):
        await service.verify_email("abc")


async def test_verify_email_rejects_expired_token():
    repo = _VerificationRepo(_token("abc", expires_in=timedelta(minutes=-1)))
    service = EmailVerificationService(_UserRepo(), repo)

    with pytest.raises(TokenExpiredException):
        await service.verify_email("abc")


async def test_verify_email_rejects_unknown_token():
    service = EmailVerificationService(_UserRepo(), _VerificationRepo(None))

    with pytest.raises(InvalidTokenException):
        await service.verify_email("abc")


async def test_resend_sends_for_unverified_user():
    verification, email = _VerificationService(), _EmailService()
    user = SimpleNamespace(id=uuid4(), email="a@example.com", is_verified=False)

    await _auth_service(user, verification, email).resend_verification("a@example.com")

    assert verification.calls == [user.id]
    assert email.sent == ["a@example.com"]


async def test_resend_stays_silent_for_unknown_email():
    verification, email = _VerificationService(), _EmailService()

    await _auth_service(None, verification, email).resend_verification("b@example.com")

    assert verification.calls == []
    assert email.sent == []


async def test_resend_stays_silent_for_verified_user():
    verification, email = _VerificationService(), _EmailService()
    user = SimpleNamespace(id=uuid4(), email="c@example.com", is_verified=True)

    await _auth_service(user, verification, email).resend_verification("c@example.com")

    assert verification.calls == []
    assert email.sent == []


async def test_resend_raises_when_email_send_fails():
    """Gửi mail hỏng phải báo lỗi, để get_db rollback và giữ lại token cũ."""
    verification, email = _VerificationService(), _EmailService(ok=False)
    user = SimpleNamespace(id=uuid4(), email="d@example.com", is_verified=False)

    with pytest.raises(EmailSendFailedException):
        await _auth_service(user, verification, email).resend_verification("d@example.com")
