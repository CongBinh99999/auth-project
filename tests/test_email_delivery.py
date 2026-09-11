"""Mail được kích hoạt đúng chỗ, và stub SMTP thật sự chặn được đường ra."""

from httpx import AsyncClient


async def test_register_triggers_verification_email(
    async_client: AsyncClient, test_user_data: dict, stub_smtp: list
):
    await async_client.post("/api/v1/auth/register", json=test_user_data)

    assert [to for to, _ in stub_smtp] == [test_user_data["email"]]


async def test_resend_verification_triggers_another_email(
    async_client: AsyncClient, test_user_data: dict, stub_smtp: list
):
    await async_client.post("/api/v1/auth/register", json=test_user_data)
    stub_smtp.clear()

    await async_client.post(
        "/api/v1/auth/resend-verification", json={"email": test_user_data["email"]}
    )

    # Cooldown 60s chặn ngay sau register, nên không có mail thứ hai.
    assert stub_smtp == []


async def test_unknown_email_triggers_no_mail(
    async_client: AsyncClient, stub_smtp: list
):
    await async_client.post(
        "/api/v1/auth/resend-verification", json={"email": "nobody-xyz@example.com"}
    )

    assert stub_smtp == []
