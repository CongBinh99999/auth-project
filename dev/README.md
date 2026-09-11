# Dev console

Trang HTML tĩnh để thử luồng auth bằng tay và chạy các kịch bản bảo mật.
Không thuộc ứng dụng, không được import ở bất kỳ đâu trong `app/`.

## Chạy

Hai tiến trình, hai terminal:

```bash
uv run uvicorn app.main:app --reload          # API ở :8000
python3 -m http.server 5173 -d dev            # console ở :5173
```

Mở http://localhost:5173/console.html

## Vì sao phải qua cổng 5173

`CORS_ORIGINS` chỉ cho `http://localhost:3000` và `http://localhost:5173`.
Mở file trực tiếp bằng `file://` sẽ gửi `Origin: null` và bị CORS chặn, nên
phải phục vụ qua HTTP ở đúng một trong hai cổng đó.

## Lấy token xác thực ở đâu

Token chỉ tồn tại trong email — đúng thiết kế, database chỉ lưu hash. Cấu hình
SMTP trong `.env` rồi dán link trong mail vào ô "Token xác thực"; trang tự cắt
phần `?token=`.

Không có SMTP thì đánh dấu verified thẳng trong database:

```sql
update users set is_verified = true where email = '<email>';
```

## Lưu ý về hạn mức

Kịch bản "Đăng ký liên tiếp" dùng hết hạn mức 10 đăng ký mỗi 60 phút của IP,
nên nó đứng cuối danh sách. Chạy nó xong thì các kịch bản khác không tạo được
tài khoản mới cho tới khi hết cửa sổ. Muốn thử lại ngay:

```sql
delete from login_attempts;
```
