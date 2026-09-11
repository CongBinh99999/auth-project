"""Register throttle - một IP không được tạo tài khoản không giới hạn."""

import pytest

from app.core.exceptions import TooManyRegistrationsException
from app.services.auth_service import AuthService
from app.services.login_attempt_service import LoginAttemptService


class _Session:
    async def commit(self):
        pass


class _UserRepo:
    def __init__(self):
        self.db = _Session()

    async def get_by_email(self, email):
        raise AssertionError("throttle phải chặn trước khi chạm tới database")


class _AttemptService:
    def __init__(self, throttled):
        self.throttled = throttled

    async def is_registration_throttled(self, ip_address):
        return self.throttled


class _AttemptRepo:
    def __init__(self, count):
        self.count = count
        self.asked = []

    async def count_registrations_by_ip(self, ip_address, minutes):
        self.asked.append((ip_address, minutes))
        return self.count


async def test_register_is_rejected_when_ip_is_throttled():
    service = AuthService(
        _UserRepo(), None, None, None, _AttemptService(True), None, None
    )

    with pytest.raises(TooManyRegistrationsException) as exc:
        await service.register("a@example.com", "TestPassword123!", None, "1.2.3.4")

    assert exc.value.status_code == 429


async def test_throttle_trips_at_the_limit():
    service = LoginAttemptService(_AttemptRepo(LoginAttemptService.MAX_REGISTRATIONS_PER_IP))

    assert await service.is_registration_throttled("1.2.3.4") is True


async def test_throttle_allows_below_the_limit():
    repo = _AttemptRepo(LoginAttemptService.MAX_REGISTRATIONS_PER_IP - 1)
    service = LoginAttemptService(repo)

    assert await service.is_registration_throttled("1.2.3.4") is False
    assert repo.asked == [("1.2.3.4", LoginAttemptService.REGISTRATION_WINDOW_MINUTES)]
