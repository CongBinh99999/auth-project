"""Chặn thiết bị - phải thật sự chặn, và phải gỡ được."""

from uuid import uuid4

import pytest

from app.core.exceptions import DeviceBlockedException
from app.core.security import device_fingerprint
from app.services.device_service import DeviceService
from app.utils.constants import DeviceStatus


class _Device:
    def __init__(self, status=DeviceStatus.ACTIVE):
        self.id = uuid4()
        self.status = status


class _DeviceRepo:
    def __init__(self, existing=None):
        self.existing = existing
        self.created = 0

    async def get_by_fingerprint(self, user_id, fingerprint):
        return self.existing

    async def get_device_by_id(self, device_id, user_id):
        return self.existing

    async def create(self, **data):
        self.created += 1
        return _Device()

    async def update(self, device, **data):
        return device

    async def set_status(self, device, status):
        device.status = status
        return device


def test_fingerprint_is_stable_for_the_same_user_agent():
    ua = "Mozilla/5.0 TestBrowser"

    assert device_fingerprint(ua) == device_fingerprint(ua)
    assert device_fingerprint(ua) != device_fingerprint("Other/1.0")
    assert device_fingerprint(None) == device_fingerprint(None)


async def test_login_from_a_blocked_device_is_refused():
    repo = _DeviceRepo(_Device(DeviceStatus.BLOCKED))
    service = DeviceService(repo)

    with pytest.raises(DeviceBlockedException) as exc:
        await service.register_device(user_id=uuid4(), fingerprint="fp")

    assert exc.value.status_code == 403
    assert repo.created == 0, "device bị chặn không được tạo bản ghi mới để lách"


async def test_login_from_an_active_device_is_allowed():
    repo = _DeviceRepo(_Device(DeviceStatus.ACTIVE))

    await DeviceService(repo).register_device(user_id=uuid4(), fingerprint="fp")

    assert repo.created == 0, "device đã có thì cập nhật, không tạo thêm"


async def test_unknown_device_is_created_once():
    repo = _DeviceRepo(None)

    await DeviceService(repo).register_device(user_id=uuid4(), fingerprint="fp")

    assert repo.created == 1


async def test_block_then_unblock_restores_access():
    device = _Device()
    repo = _DeviceRepo(device)
    service = DeviceService(repo)
    user_id = uuid4()

    await service.block_device(device.id, user_id)
    assert device.status == DeviceStatus.BLOCKED

    await service.unblock_device(device.id, user_id)
    assert device.status == DeviceStatus.ACTIVE
