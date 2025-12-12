# Purpose: Database model for Token Families (Refresh Token Rotation).

from datetime import datetime,timezone
import uuid
from sqlmodel.main import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING: 
    from app.models.user import User 
    from app.models.user_device import UserDevice

class TokenFamily(SQLModel, table=True):
    __tablename__="token_families"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    device_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user_devices.id")
    current_jti: str = Field(max_length=36)
    is_revoked: bool = Field(default=False)
    created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    last_used_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    #relationship 
    user: Optional["User"] = Relationship(back_populates="token_families")
    device: Optional["UserDevice"] = Relationship(back_populates="token_families")


