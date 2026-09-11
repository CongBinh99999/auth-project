
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 
    
    APP_NAME: str = "AuthProject"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = "postgresql+asyncpg://postgres:123@localhost:5432/mysens"

    JWT_SECRET: str = "SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 

    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 15
    
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TIMEOUT: int = 10

    RESEND_VERIFICATION_COOLDOWN_SECONDS: int = 60
    PASSWORD_RESET_COOLDOWN_SECONDS: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:3000","http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def _reject_placeholder_secret(self) -> "Settings":  # noqa: UP037
        """Không cho chạy ngoài development với JWT_SECRET mẫu.

        Secret mẫu nằm sẵn trong .env.example và trong default của chính class
        này, nên rất dễ đi thẳng lên server. Ai biết nó thì ký được token của
        bất kỳ user nào.
        """
        placeholders = {"", "SECRET_KEY", "change_this_to_a_secure_random_string"}

        if self.APP_ENV == "development":
            if self.JWT_SECRET in placeholders:
                print("[CONFIG] JWT_SECRET đang là giá trị mẫu - chỉ chấp nhận ở development")
            return self

        if self.JWT_SECRET in placeholders or len(self.JWT_SECRET) < 32:
            # RuntimeError chứ không phải ValueError: pydantic bọc ValueError
            # thành ValidationError và in kèm toàn bộ input, trong đó có
            # SMTP_PASSWORD. RuntimeError thoát thẳng ra, không lộ gì.
            raise RuntimeError(
                f"JWT_SECRET không hợp lệ cho APP_ENV={self.APP_ENV}: "
                "phải đặt giá trị riêng, tối thiểu 32 ký tự"
            )

        return self


@lru_cache
def get_settings() -> Settings: 
    return Settings()