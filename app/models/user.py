# Purpose: Database model for Users.

from typing import List
from sqlmodel.main import SQLModel, Field, Relationship
import uuid
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING: 
    from app.models.role import Role
    from app.models.token_family import TokenFamily
    from app.models.user_device import UserDevice
    from app.models.login_attempt import LoginAttempt
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.password_reset_token import PasswordResetToken
    from app.models.token_blacklist import TokenBlacklist
    from app.models.token_family import TokenFamily

class User(SQLModel, table=True): 
    __tablename__="users"
    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True)
    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role_id: uuid.UUID = Field(foreign_key="roles.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = Field(default=None, nullable=True)

    #relationship 
    role: Optional["Role"] = Relationship(back_populates="users")
    token_families: List["TokenFamily"] = Relationship(back_populates="user")
    devices: List["UserDevice"] = Relationship(back_populates="user")
    login_attempts: List["LoginAttempt"] = Relationship(back_populates="user")
    email_verification_tokens: List["EmailVerificationToken"] = Relationship(back_populates="user")
    password_reset_tokens:List["PasswordResetToken"] = Relationship(back_populates="user") 
    token_blacklists: List["TokenBlacklist"] = Relationship(back_populates="user")


