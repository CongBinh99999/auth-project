import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User

from sqlalchemy import DateTime


class EmailVerificationToken(SQLModel, table=True):
    __tablename__ ="email_verification_tokens"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str = Field(max_length=255)
    email: str = Field(max_length=255)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True))
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))
    verified_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))

    #relationship
    user: Optional["User"] = Relationship(back_populates="email_verification_tokens")