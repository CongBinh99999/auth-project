from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING: 
    from app.models.user import User

class LoginAttempt(SQLModel, table=True): 
    __tablename__ ="login_attempts"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    email: str = Field(max_length=255)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    ip_address: str = Field(max_length=45)
    user_agent: Optional[str] = None 
    is_successful: bool = Field(default=False)
    failure_reason: Optional[str] = Field(max_length=100, default=None)
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    #relationship
    user:Optional["User"] = Relationship(back_populates="login_attempts")
    