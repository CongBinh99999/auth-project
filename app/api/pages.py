"""Trang HTML phục vụ trực tiếp từ API.

Chỉ có một trang: form đặt lại mật khẩu. Link trong email reset trỏ tới
`{base_url}/reset-password`, tức gốc domain chứ không phải dưới /api/v1, và
không thể là GET thuần vì người dùng phải nhập mật khẩu mới.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(include_in_schema=False)

_PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Đặt lại mật khẩu</title>
<style>
  :root { color-scheme: light dark; }
  body {
    margin: 0; min-height: 100vh; display: grid; place-items: center;
    background: Canvas; color: CanvasText;
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  form {
    width: min(100% - 32px, 380px); padding: 28px;
    border: 1px solid color-mix(in srgb, CanvasText 14%, transparent);
    border-radius: 12px;
  }
  h1 { font-size: 18px; margin: 0 0 4px; }
  p.sub { margin: 0 0 20px; opacity: .65; font-size: 13px; }
  label { display: block; font-size: 13px; margin: 14px 0 5px; }
  input {
    width: 100%; box-sizing: border-box; padding: 9px 11px; font: inherit;
    border: 1px solid color-mix(in srgb, CanvasText 20%, transparent);
    border-radius: 7px; background: Canvas; color: CanvasText;
  }
  button {
    width: 100%; margin-top: 20px; padding: 10px; font: inherit; font-weight: 600;
    border: 0; border-radius: 7px; background: CanvasText; color: Canvas; cursor: pointer;
  }
  button:disabled { opacity: .5; cursor: default; }
  #msg { margin-top: 16px; font-size: 13px; min-height: 1.5em; }
  #msg.ok { color: #0f7b45; }
  #msg.bad { color: #b42318; }
</style>
</head>
<body>
<form id="f">
  <h1>Đặt lại mật khẩu</h1>
  <p class="sub">Nhập mật khẩu mới cho tài khoản của bạn.</p>

  <label for="p1">Mật khẩu mới</label>
  <input id="p1" type="password" autocomplete="new-password" minlength="8" required>

  <label for="p2">Nhập lại mật khẩu</label>
  <input id="p2" type="password" autocomplete="new-password" minlength="8" required>

  <button type="submit">Đặt lại mật khẩu</button>
  <div id="msg"></div>
</form>

<script>
// Đọc thẳng từ URL. Server không chèn gì vào trang, nên token mang HTML
// cũng không thoát ra ngoài được.
const token = new URLSearchParams(location.search).get("token") || "";
const msg = document.getElementById("msg");
const button = document.querySelector("button");

function say(kind, text) {
  msg.className = kind;
  msg.textContent = text;
}

if (!token) {
  say("bad", "Link thiếu token. Hãy mở đúng link trong email.");
  button.disabled = true;
}

document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();

  const p1 = document.getElementById("p1").value;
  const p2 = document.getElementById("p2").value;

  if (p1 !== p2) {
    say("bad", "Hai mật khẩu không khớp.");
    return;
  }

  button.disabled = true;
  say("", "Đang gửi...");

  let res;
  try {
    res = await fetch("/api/v1/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token, new_password: p1, confirm_password: p2 }),
    });
  } catch (err) {
    // Không bắt ở đây thì nút kẹt ở "Đang gửi..." vĩnh viễn.
    say("bad", "Không gọi được máy chủ. Kiểm tra kết nối rồi thử lại.");
    button.disabled = false;
    return;
  }

  if (res.ok) {
    say("ok", "Xong. Mọi phiên đăng nhập cũ đã bị thu hồi, hãy đăng nhập lại.");
    return;
  }

  const body = await res.json().catch(() => null);
  const detail = body && typeof body.detail === "string" ? body.detail : null;
  say("bad", detail || "Mật khẩu không hợp lệ hoặc link đã hết hạn.");
  button.disabled = false;
});
</script>
</body>
</html>
"""


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page() -> HTMLResponse:
    """Form đặt lại mật khẩu, đích đến của link trong email.

    Trang hoàn toàn tĩnh. Token nằm trong query string và do JS phía client
    đọc lấy; server không nội suy gì vào HTML.
    """
    return HTMLResponse(_PAGE)
