
from datetime import datetime, timezone
from sqlalchemy import Column, Enum as SAEnum, DateTime
from typing import Optional, TYPE_CHECKING
from app.utils.constants import TokenType
from enum import Enum
import uuid
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING: 
    from app.models.user import User 

from sqlalchemy import DateTime

class TokenBlacklist(SQLModel, table=True):
    __tablename__="token_blacklist"
    id: Optional[int] = Field(default_factory=None, primary_key=True)
    jti: str = Field(max_length=36, unique=True)
    token_type: str = Field(
        sa_column=Column(
            SAEnum (
                TokenType, 
                name='token_type', 
                create_type=False,    
                native_enum=True, 
                values_callable=lambda x: [e.value for e in x]
            ), 
            nullable=False
        )
        
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    reason: Optional[str] = Field(default=None, max_length=100)

    #relationship 
    user: Optional["User"] = Relationship(back_populates="token_blacklists")
    

    

