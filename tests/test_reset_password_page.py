"""Trang đặt lại mật khẩu - tĩnh hoàn toàn, không nhận dữ liệu từ query."""

import re

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


def _script(html: str) -> str:
    return re.search(r"<script>(.*)</script>", html, re.S).group(1)


async def test_script_has_no_leftover_brace_escaping(async_client: AsyncClient):
    """_PAGE là chuỗi thường, không phải template.

    Bản đầu tiên còn sót {{ }} từ lúc nó là f-string. Trang vẫn render, nên
    ảnh chụp trông bình thường, nhưng script lỗi cú pháp và nút không làm gì.
    """
    js = _script((await async_client.get("/reset-password")).text)

    assert "{{" not in js
    assert "}}" not in js


async def test_script_braces_are_balanced(async_client: AsyncClient):
    js = _script((await async_client.get("/reset-password")).text)

    assert js.count("{") == js.count("}")
    assert js.count("(") == js.count(")")


async def test_script_posts_to_the_reset_endpoint(async_client: AsyncClient):
    js = _script((await async_client.get("/reset-password")).text)

    assert "/api/v1/auth/reset-password" in js
    assert "catch" in js, "fetch phải có nhánh lỗi, nếu không nút kẹt ở 'Đang gửi...'"
