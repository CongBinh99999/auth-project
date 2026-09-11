"""Brute-force protection - lần thất bại phải được lưu, ngưỡng email/IP tách riêng."""

import pytest

from app.core.exceptions import InvalidCredentialsException
from app.services.auth_service import AuthService
from app.services.login_attempt_service import LoginAttemptService


class _Session:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


class _UserRepo:
    """get_by_email trả None -> authenticate_user raise InvalidCredentialsException."""

    def __init__(self):
        self.db = _Session()

    async def get_by_email(self, email):
        return None


class _AttemptService:
    def __init__(self, blocked=False):
        self.blocked = blocked
        self.recorded = []

    async def is_blocked(self, email, ip_address):
        return self.blocked

    async def record_attempt(self, email, ip, ok, user_id, user_agent, reason=None):
        self.recorded.append((email, ok, reason))


class _AttemptRepo:
    """Đếm theo từng tiêu chí, như repo thật sau khi tách ngưỡng."""

    def __init__(self, by_email=0, by_ip=0):
        self.by_email = by_email
        self.by_ip = by_ip

    async def is_blocked(self, email, ip_address, max_per_email, max_per_ip):
        if self.by_email >= max_per_email:
            return True
        return self.by_ip >= max_per_ip


def _auth_service(attempts):
    return AuthService(_UserRepo(), None, None, None, attempts, None, None)


async def test_failed_login_is_recorded_and_committed():
    """get_db rollback khi request raise, nên lần thất bại phải commit ngay."""
    attempts = _AttemptService()
    service = _auth_service(attempts)

    with pytest.raises(InvalidCredentialsException):
        await service.login("a@example.com", "wrong", "1.2.3.4")

    assert attempts.recorded == [("a@example.com", False, "invalid_credentials")]
    assert service.user_repo.db.commits == 1


async def test_blocked_login_is_rejected_before_checking_password():
    attempts = _AttemptService(blocked=True)
    service = _auth_service(attempts)

    with pytest.raises(Exception) as exc:
        await service.login("a@example.com", "TestPassword123!", "1.2.3.4")

    assert exc.value.status_code == 429
    assert attempts.recorded == []


async def test_email_threshold_blocks_only_that_email():
    service = LoginAttemptService(_AttemptRepo(by_email=5, by_ip=5))

    assert await service.is_blocked("a@example.com", "1.2.3.4") is True


async def test_other_user_on_same_ip_is_not_blocked():
    """5 lần sai của một email không được khoá người khác cùng NAT."""
    service = LoginAttemptService(_AttemptRepo(by_email=0, by_ip=5))

    assert await service.is_blocked("b@example.com", "1.2.3.4") is False


async def test_ip_threshold_blocks_wide_scan():
    service = LoginAttemptService(_AttemptRepo(by_email=0, by_ip=20))

    assert await service.is_blocked("c@example.com", "1.2.3.4") is True
