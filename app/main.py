import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.pages import router as pages_router
from app.api.router import api_router
from app.config import get_settings
from app.config.database import AsyncSessionLocal
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.repositories.login_attempt_repository import LoginAttemptRepository
from app.repositories.password_reset_repository import PasswordResetRepository
from app.repositories.token_blacklist_repository import TokenBlacklistRepository

settings = get_settings()

CLEANUP_INTERVAL_SECONDS = 60 * 60


async def purge_expired() -> dict[str, int]:
    """Xoá token hết hạn và login attempt cũ.

    Mọi repository đều có sẵn hàm dọn nhưng trước đây không ai gọi, nên các
    bảng này chỉ lớn lên chứ không bao giờ nhỏ lại.
    """
    async with AsyncSessionLocal() as session:
        removed = {
            "email_verification": await EmailVerificationRepository(session).cleanup_expired(),
            "password_reset": await PasswordResetRepository(session).cleanup_expired(),
            "token_blacklist": await TokenBlacklistRepository(session).cleanup_expired(),
            "login_attempts": await LoginAttemptRepository(session).cleanup_old_attempts(),
        }
        await session.commit()

    return removed


async def cleanup_loop() -> None:
    """Chạy purge_expired định kỳ suốt vòng đời ứng dụng."""
    while True:
        try:
            print(f"[CLEANUP] {await purge_expired()}")
        except Exception as e:  # noqa: BLE001 - vòng lặp dọn dẹp không được phép chết
            print(f"[CLEANUP] thất bại: {e}")

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI): 
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    cleanup = asyncio.create_task(cleanup_loop())

    yield

    cleanup.cancel()
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION, 
    debug=settings.APP_DEBUG, 
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(pages_router)

@app.get("/health")
async def health_check(): 
    return {
        "status": "healthy", 
        "app": settings.APP_NAME, 
        "version": settings.APP_VERSION
    }

if __name__ == "__main__": 
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.APP_HOST, 
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )
