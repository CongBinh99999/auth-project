import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel.main import Field, Relationship, SQLModel

if TYPE_CHECKING: 
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.login_attempt import LoginAttempt
    from app.models.password_reset_token import PasswordResetToken
    from app.models.role import Role
    from app.models.token_blacklist import TokenBlacklist
    from app.models.token_family import TokenFamily
    from app.models.user_device import UserDevice

class User(SQLModel, table=True): 
    __tablename__="users"
    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True)
    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role_id: uuid.UUID = Field(foreign_key="roles.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True))
    last_login_at: Optional[datetime] = Field(default=None, nullable=True, sa_type=DateTime(timezone=True))

    #relationship 
    role: Optional["Role"] = Relationship(back_populates="users")
    token_families: list["TokenFamily"] = Relationship(back_populates="user")
    devices: list["UserDevice"] = Relationship(back_populates="user")
    login_attempts: list["LoginAttempt"] = Relationship(back_populates="user")
    email_verification_tokens: list["EmailVerificationToken"] = Relationship(back_populates="user")
    password_reset_tokens:list["PasswordResetToken"] = Relationship(back_populates="user") 
    token_blacklists: list["TokenBlacklist"] = Relationship(back_populates="user")


