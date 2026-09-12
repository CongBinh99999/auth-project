"""Trang đặt lại mật khẩu - tĩnh hoàn toàn, không nhận dữ liệu từ query."""

from httpx import AsyncClient

XSS = '</script><img src=x onerror=alert(1)>'


async def test_page_is_served(async_client: AsyncClient):
    res = await async_client.get("/reset-password", params={"token": "abc"})

    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]


async def test_token_is_read_from_the_url_by_the_client(async_client: AsyncClient):
    res = await async_client.get("/reset-password")

    assert "URLSearchParams(location.search)" in res.text


async def test_query_cannot_reach_the_html(async_client: AsyncClient):
    """Trang không nội suy gì, nên token mang HTML cũng không thoát ra được."""
    plain = await async_client.get("/reset-password", params={"token": "abc"})
    hostile = await async_client.get("/reset-password", params={"token": XSS})

    assert hostile.text == plain.text
    assert "onerror=alert" not in hostile.text


async def test_page_is_hidden_from_the_openapi_schema(async_client: AsyncClient):
    schema = (await async_client.get("/openapi.json")).json()

    assert "/reset-password" not in schema["paths"]
