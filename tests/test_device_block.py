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


class _FamilyRepo:
    def __init__(self):
        self.revoked = []

    async def revoke_all_for_device(self, device_id):
        self.revoked.append(device_id)
        return 1


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
    service = DeviceService(repo, _FamilyRepo())
    user_id = uuid4()

    await service.block_device(device.id, user_id)
    assert device.status == DeviceStatus.BLOCKED

    await service.unblock_device(device.id, user_id)
    assert device.status == DeviceStatus.ACTIVE


async def test_duplicate_fingerprints_do_not_break_login():
    """Không có ràng buộc unique trên (user_id, fingerprint).

    Hai login đồng thời có thể cùng tạo một dòng. Trước đây lookup dùng
    scalar_one_or_none() nên từ đó trở đi mọi lần đăng nhập đều trả 500.
    """
    blocked = _Device(DeviceStatus.BLOCKED)

    class _DuplicateRepo(_DeviceRepo):
        async def get_by_fingerprint(self, user_id, fingerprint):
            # repo thật dùng .first() nên luôn trả đúng một dòng, không ném lỗi
            return blocked

    with pytest.raises(DeviceBlockedException):
        await DeviceService(_DuplicateRepo()).register_device(user_id=uuid4(), fingerprint="fp")


async def test_blocking_revokes_the_device_sessions():
    """Đổi cờ thôi là chưa đủ - phiên đang chạy trên device đó phải chết.

    Nếu không, điện thoại bị mất vẫn refresh token vô hạn sau khi chủ máy
    bấm chặn.
    """
    device = _Device()
    families = _FamilyRepo()

    await DeviceService(_DeviceRepo(device), families).block_device(device.id, uuid4())

    assert families.revoked == [device.id]


async def test_unblock_leaves_a_non_blocked_device_alone():
    """Endpoint này chỉ gỡ chặn, không phải nút 'đặt trạng thái active'."""
    device = _Device(DeviceStatus.INACTIVE)

    await DeviceService(_DeviceRepo(device), _FamilyRepo()).unblock_device(device.id, uuid4())

    assert device.status == DeviceStatus.INACTIVE
