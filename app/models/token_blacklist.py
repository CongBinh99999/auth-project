from datetime import datetime, timezone
from sqlmodel.main import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum
import uuid

if TYPE_CHECKING: 
    from app.models.user import User 

# Kế thừa (str, Enum) giúp nó vừa là Enum vừa hoạt động như string
class TokenType(str, Enum): 
    ACCESS = "access"
    REFRESH = "refresh"



class TokenBlacklist(SQLModel, table=True):
    __tablename__="token_blacklist"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    jti: str = Field(max_length=36, unique=True)
    token_type: TokenType = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    expires_at: datetime
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = Field(default=None, max_length=100)

    #relationship 
    user: Optional["User"] = Relationship(back_populates="token_blacklists")
    

    

