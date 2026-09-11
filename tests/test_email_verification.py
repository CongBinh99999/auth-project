"""Email verification - token dùng một lần, resend không lộ email và không spam."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import InvalidTokenException, TokenExpiredException
from app.core.security import hash_verification_token
from app.services.auth_service import AuthService
from app.services.email_verification_service import EmailVerificationService


class _Session:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class _UserRepo:
    def __init__(self, user=None):
        self.user = user
        self.verified = []
        self.db = _Session()

    async def get_by_email(self, email):
        return self.user

    async def get_by_id(self, user_id):
        return self.user

    async def verify_by_id(self, user_id):
        self.verified.append(user_id)


class _VerificationRepo:
    """Giả lập UPDATE có điều kiện: chỉ request đầu tiên giành được token."""

    def __init__(self, token=None):
        self.token = token
        self.deleted = []
        self.created = 0

    async def mark_verified_if_unused(self, token_hash):
        t = self.token
        if t is None or t.token_hash != token_hash or t.verified_at is not None:
            return None
        t.verified_at = datetime.now(UTC)
        return t.user_id, t.expires_at

    async def get_pending_by_user(self, user_id):
        return self.token

    async def delete_by_user(self, user_id):
        self.deleted.append(user_id)
        self.token = None

    async def create(self, **data):
        self.created += 1
        return SimpleNamespace(**data)


class _VerificationService:
    def __init__(self, token="plain-token"):
        self.token = token
        self.calls = []

    async def resend_email(self, user_id):
        self.calls.append(user_id)
        return self.token


class _EmailService:
    def send_verification_email(self, to_email, token):
        return True


class _BackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, **kwargs):
        self.tasks.append(kwargs)


def _token(plain, *, verified_at=None, expires_in=timedelta(minutes=15), age=timedelta(0)):
    return SimpleNamespace(
        user_id=uuid4(),
        token_hash=hash_verification_token(plain),
        verified_at=verified_at,
        expires_at=datetime.now(UTC) + expires_in,
        created_at=datetime.now(UTC) - age,
    )


def _auth_service(user, verification):
    return AuthService(_UserRepo(user), None, None, None, None, verification, _EmailService())


async def test_resend_commits_before_scheduling_mail():
    """Mail chỉ được lên lịch sau khi transaction đã commit."""
    verification, tasks = _VerificationService(), _BackgroundTasks()
    user = SimpleNamespace(id=uuid4(), email="g@example.com", is_verified=False)
    service = _auth_service(user, verification)

    await service.resend_verification("g@example.com", tasks)

    assert service.user_repo.db.commits == 1


async def test_verify_email_accepts_fresh_token():
    users = _UserRepo()
    service = EmailVerificationService(users, _VerificationRepo(_token("abc")))

    assert await service.verify_email("abc") is True
    assert users.verified


async def test_verify_email_rejects_used_token():
    service = EmailVerificationService(
        _UserRepo(), _VerificationRepo(_token("abc", verified_at=datetime.now(UTC)))
    )

    with pytest.raises(InvalidTokenException):
        await service.verify_email("abc")


async def test_verify_email_rejects_expired_token():
    service = EmailVerificationService(
        _UserRepo(), _VerificationRepo(_token("abc", expires_in=timedelta(minutes=-1)))
    )

    with pytest.raises(TokenExpiredException):
        await service.verify_email("abc")


async def test_verify_email_rejects_unknown_token():
    service = EmailVerificationService(_UserRepo(), _VerificationRepo(None))

    with pytest.raises(InvalidTokenException):
        await service.verify_email("abc")


async def test_second_concurrent_verify_loses_the_race():
    """Request thứ hai trên cùng token phải trượt, không được verify hai lần."""
    users = _UserRepo()
    service = EmailVerificationService(users, _VerificationRepo(_token("abc")))

    assert await service.verify_email("abc") is True
    with pytest.raises(InvalidTokenException):
        await service.verify_email("abc")
    assert len(users.verified) == 1


async def test_resend_schedules_mail_in_background():
    verification, tasks = _VerificationService(), _BackgroundTasks()
    user = SimpleNamespace(id=uuid4(), email="a@example.com", is_verified=False)

    await _auth_service(user, verification).resend_verification("a@example.com", tasks)

    assert verification.calls == [user.id]
    assert tasks.tasks == [{"to_email": "a@example.com", "token": "plain-token"}]


async def test_resend_stays_silent_for_unknown_email():
    verification, tasks = _VerificationService(), _BackgroundTasks()

    await _auth_service(None, verification).resend_verification("b@example.com", tasks)

    assert verification.calls == []
    assert tasks.tasks == []


async def test_resend_stays_silent_for_verified_user():
    verification, tasks = _VerificationService(), _BackgroundTasks()
    user = SimpleNamespace(id=uuid4(), email="c@example.com", is_verified=True)

    await _auth_service(user, verification).resend_verification("c@example.com", tasks)

    assert verification.calls == []
    assert tasks.tasks == []


async def test_resend_sends_nothing_while_in_cooldown():
    """Token vừa phát chưa lâu -> không gửi thêm mail."""
    verification, tasks = _VerificationService(token=None), _BackgroundTasks()
    user = SimpleNamespace(id=uuid4(), email="d@example.com", is_verified=False)

    await _auth_service(user, verification).resend_verification("d@example.com", tasks)

    assert tasks.tasks == []


async def test_resend_email_respects_cooldown():
    repo = _VerificationRepo(_token("old", age=timedelta(seconds=5)))
    user = SimpleNamespace(id=uuid4(), email="e@example.com")
    service = EmailVerificationService(_UserRepo(user), repo)

    assert await service.resend_email(user.id) is None
    assert repo.deleted == []


async def test_resend_email_issues_new_token_after_cooldown():
    repo = _VerificationRepo(_token("old", age=timedelta(minutes=5)))
    user = SimpleNamespace(id=uuid4(), email="f@example.com")
    service = EmailVerificationService(_UserRepo(user), repo)

    assert await service.resend_email(user.id) is not None
    assert repo.deleted == [user.id]
