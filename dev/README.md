# Dev console

Ứng dụng React dùng để thử luồng auth bằng tay và chạy các kịch bản bảo mật.
Chỉ phục vụ việc phát triển — không có gì trong `app/` import từ đây, và CI
không build thư mục này.

## Chạy

`docker compose up -d --build` ở thư mục gốc đã phục vụ sẵn console tại
http://localhost:5173 (bản build tĩnh, không hot reload). Phần dưới là cách
chạy với hot reload để sửa chính console.

Hai tiến trình, hai terminal:

```bash
uv run uvicorn app.main:app --reload   # API ở :8000
cd dev && npm install && npm run dev   # console ở :5173
```

Mở http://localhost:5173

## Vì sao phải là cổng 5173

`CORS_ORIGINS` chỉ cho `http://localhost:3000` và `http://localhost:5173`.
`vite.config.ts` đặt `strictPort: true` để Vite báo lỗi thay vì âm thầm nhảy
sang cổng khác rồi bị CORS chặn.

## Lấy token xác thực ở đâu

Token chỉ tồn tại trong email — database chỉ lưu hash, đúng thiết kế.

Điền "Hộp thư nhận" bằng địa chỉ thật của bạn. Nút làm mới sẽ sinh email test
dạng plus-addressing (`ban+dev_xxx@gmail.com`), mọi mail đều về đúng hộp thư đó
mà mỗi lần đăng ký vẫn là một tài khoản mới. Giá trị này lưu trong localStorage.

Để trống thì email test rơi về `@example.com`. Tên miền đó không có bản ghi MX
nên Gmail trả lại ngay — chỉ dùng được khi không cần đọc mail, và gửi nhiều thì
ảnh hưởng uy tín người gửi.

Nhận được mail thì dán cả link vào ô "Token xác thực"; app tự cắt phần `?token=`.

Không cấu hình SMTP thì đánh dấu verified thẳng trong database:

```sql
update users set is_verified = true where email = '<email>';
```

## Hạn mức khi chạy kịch bản

Kịch bản "Đăng ký liên tiếp từ cùng IP" dùng hết hạn mức 10 đăng ký mỗi 60 phút,
nên nó đứng cuối danh sách và "Chạy tất cả" chạy nó sau cùng. Chạy xong thì các
kịch bản khác không tạo được tài khoản mới cho tới khi hết cửa sổ. Muốn thử lại
ngay:

```sql
delete from login_attempts;
```

## Cấu trúc

```
src/lib/api.ts         fetch wrapper, decode JWT, phát sự kiện cho nhật ký
src/lib/scenarios.ts   6 kịch bản bảo mật, mỗi cái tự khẳng định đúng/sai
src/components/        token card, nhật ký request, danh sách kịch bản
src/components/ui/     component shadcn (preset radix-nova)
```
