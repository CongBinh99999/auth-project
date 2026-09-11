from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import SQLModel

from app.config.settings import get_settings

settings = get_settings()

class Base(DeclarativeBase): 
    pass

engine = create_async_engine(
    settings.DATABASE_URL, 
    echo = settings.APP_DEBUG, 
    future = True
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine, 
    class_ = AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession: 
    async with AsyncSessionLocal() as session: 
        try:
            yield session 
            await session.commit()
        except Exception: 
            await session.rollback()
            raise
        finally: 
            await session.close()

async def init_db(): 
    async with engine.begin() as conn: 
        await conn.run_sync(SQLModel.metadata.create_all)


"""
DATABASE LAYER – IMPORTANT NOTES

1. engine
- Là nơi biết đường kết nối tới database và quản lý connection pool
- Đóng vai trò trung gian để SQL được gửi tới database
- Không phải nơi viết logic query, nhưng SQL muốn chạy bắt buộc phải thông qua engine
- Session sẽ mượn connection từ engine để làm việc

2. AsyncSessionLocal
- Là nơi tạo ra các session khác nhau (session factory)
- Mỗi lần gọi AsyncSessionLocal() → tạo 1 AsyncSession mới
- Mỗi session đại diện cho một lần làm việc với database (thường là 1 request)
- Không dùng chung session cho nhiều request

3. AsyncSession
- Là phiên làm việc trực tiếp với database
- Là nơi thực sự thực hiện các câu lệnh SQL (thông qua engine)
- Quản lý transaction, trạng thái query, và dữ liệu đang được load
- Gắn với vòng đời của một request

4. get_db()
- Là dependency dùng trong FastAPI
- Giống như một công xưởng bao quát toàn bộ database layer
- Chịu trách nhiệm:
    + tạo session từ AsyncSessionLocal
    + cung cấp session cho route / service sử dụng
    + commit nếu thành công
    + rollback nếu có lỗi
    + close session sau khi xong việc
- Route / service chỉ dùng session, không tự commit

Flow chuẩn:
Request
 → get_db()
 → AsyncSession
 → engine (mượn connection)
 → Database

"""


