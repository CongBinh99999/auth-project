
from pydantic_settings import BaseSettings, SettingsConfigDict 
from functools import lru_cache

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

    CORS_ORIGINS: list[str] = ["http://localhost:3000","http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings: 
    return Settings()