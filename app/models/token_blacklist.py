
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.utils.constants import TokenType

if TYPE_CHECKING: 
    from app.models.user import User


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
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True))
    reason: Optional[str] = Field(default=None, max_length=100)

    #relationship 
    user: Optional["User"] = Relationship(back_populates="token_blacklists")
    

    

