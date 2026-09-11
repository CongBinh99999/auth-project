"""Password reset - token dùng một lần, cooldown, và thu hồi session."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import InvalidTokenException
from app.core.security import hash_verification_token
from app.services.auth_service import AuthService
from app.services.password_reset_service import PasswordResetService


class _Session:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class _UserRepo:
    def __init__(self, user=None):
        self.user = user
        self.db = _Session()
        self.passwords = []

    async def get_by_email(self, email):
        return self.user

    async def get_by_id(self, user_id):
        return self.user

    async def update_password(self, user, hashed):
        self.passwords.append(hashed)


class _ResetRepo:
    """Giả lập UPDATE có điều kiện: chỉ request đầu tiên giành được token."""

    def __init__(self, token=None):
        self.token = token
        self.deleted = []
        self.created = 0

    async def mark_used_if_unused(self, token_hash):
        t = self.token
        if t is None or t.token_hash != token_hash or t.used_at is not None:
            return None
        t.used_at = datetime.now(UTC)
        return t.user_id, t.expires_at

    async def get_pending_by_user(self, user_id):
        return self.token

    async def delete_by_user(self, user_id):
        self.deleted.append(user_id)
        self.token = None

    async def create(self, **data):
        self.created += 1
        return SimpleNamespace(**data)


class _FamilyRepo:
    def __init__(self):
        self.revoked = []

    async def revoke_all_for_user(self, user_id):
        self.revoked.append(user_id)
        return 1


class _ResetService:
    def __init__(self, token="plain-token"):
        self.token = token
        self.calls = []

    async def request_reset(self, email):
        self.calls.append(email)
        return self.token


class _EmailService:
    def send_password_reset_email(self, to_email, token):
        return True


class _BackgroundTasks:
    def __init__(self):
        self.tasks = []

    def add_task(self, func, **kwargs):
        self.tasks.append(kwargs)


def _token(plain, *, user_id=None, used_at=None, expires_in=timedelta(minutes=15), age=timedelta(0)):
    return SimpleNamespace(
        user_id=user_id or uuid4(),
        token_hash=hash_verification_token(plain),
        used_at=used_at,
        expires_at=datetime.now(UTC) + expires_in,
        created_at=datetime.now(UTC) - age,
    )


def _service(user, token):
    families = _FamilyRepo()
    users = _UserRepo(user)
    repo = _ResetRepo(token)
    return PasswordResetService(users, repo, families), users, repo, families


def _auth_service(reset_service):
    return AuthService(
        _UserRepo(), None, None, None, None, None, _EmailService(), None, reset_service
    )


async def test_reset_updates_password_and_revokes_sessions():
    user = SimpleNamespace(id=uuid4(), email="a@example.com")
    service, users, _, families = _service(user, _token("abc", user_id=user.id))

    assert await service.reset_password("abc", "NewPassword123!") is True
    assert len(users.passwords) == 1
    assert families.revoked == [user.id]


async def test_reset_rejects_used_token():
    user = SimpleNamespace(id=uuid4(), email="b@example.com")
    service, _, _, _ = _service(user, _token("abc", used_at=datetime.now(UTC)))

    with pytest.raises(InvalidTokenException):
        await service.reset_password("abc", "NewPassword123!")


async def test_reset_rejects_expired_token():
    user = SimpleNamespace(id=uuid4(), email="c@example.com")
    service, users, _, families = _service(user, _token("abc", expires_in=timedelta(minutes=-1)))

    with pytest.raises(InvalidTokenException):
        await service.reset_password("abc", "NewPassword123!")
    assert users.passwords == []
    assert families.revoked == []


async def test_reset_rejects_unknown_token():
    service, _, _, _ = _service(SimpleNamespace(id=uuid4()), None)

    with pytest.raises(InvalidTokenException):
        await service.reset_password("abc", "NewPassword123!")


async def test_second_concurrent_reset_loses_the_race():
    """Request thứ hai trên cùng token phải trượt, mật khẩu chỉ đổi một lần."""
    user = SimpleNamespace(id=uuid4(), email="d@example.com")
    service, users, _, _ = _service(user, _token("abc"))

    assert await service.reset_password("abc", "NewPassword123!") is True
    with pytest.raises(InvalidTokenException):
        await service.reset_password("abc", "Another123!")
    assert len(users.passwords) == 1


async def test_request_reset_respects_cooldown():
    user = SimpleNamespace(id=uuid4(), email="e@example.com")
    service, _, repo, _ = _service(user, _token("old", age=timedelta(seconds=5)))

    assert await service.request_reset("e@example.com") is None
    assert repo.deleted == []


async def test_request_reset_issues_new_token_after_cooldown():
    user = SimpleNamespace(id=uuid4(), email="f@example.com")
    service, _, repo, _ = _service(user, _token("old", age=timedelta(minutes=5)))

    assert await service.request_reset("f@example.com") is not None
    assert repo.deleted == [user.id]


async def test_forgot_password_schedules_mail_after_commit():
    reset_service, tasks = _ResetService(), _BackgroundTasks()
    service = _auth_service(reset_service)

    await service.request_password_reset("g@example.com", tasks)

    assert service.user_repo.db.commits == 1
    assert tasks.tasks == [{"to_email": "g@example.com", "token": "plain-token"}]


async def test_forgot_password_stays_silent_when_no_token_issued():
    """Email lạ hoặc còn cooldown -> request_reset trả None -> không gửi gì."""
    reset_service, tasks = _ResetService(token=None), _BackgroundTasks()
    service = _auth_service(reset_service)

    await service.request_password_reset("h@example.com", tasks)

    assert service.user_repo.db.commits == 0
    assert tasks.tasks == []
