from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class EmailVerificationToken(SQLModel, table=True):
    __tablename__ ="email_verification_tokens"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime 
    verified_at: Optional[datetime] = Field(default=None)

    #relationship
    user: Optional["User"] = Relationship(back_populates="email_verification_tokens")