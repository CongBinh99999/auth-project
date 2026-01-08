from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime

if TYPE_CHECKING: 
    from app.models.user import User

class PasswordResetToken(SQLModel, table=True):
    __tablename__="password_reset_tokens"
    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash:str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))
    used_at: Optional[datetime] = Field(default=None, nullable=True, sa_type=DateTime(timezone=True))

    # Relationship
    user:"User" = Relationship(back_populates="password_reset_tokens")
    