# Purpose: Database model for User Devices (Device Management).

import uuid
from sqlmodel.main import SQLModel, Field,  Relationship
from typing import Optional, TYPE_CHECKING, List
from enum import Enum
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.token_family import TokenFamily

class StatusType(str, Enum): 
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"

class UserDevice(SQLModel, table=True):
    __tablename__="user_devices"
    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    device_name: Optional[str] = Field(default=None, max_length=255)
    device_type: Optional[str] = Field(default=None, max_length=50)
    browser: Optional[str] = Field(default=None, max_length=100)
    os:Optional[str] = Field(default=None, max_length=100)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    fingerprint: Optional[str] = Field(default=None, max_length=255)
    status: StatusType = Field(default="active", max_length=20)
    is_trusted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 

    #relationship 
    user: Optional["User"]  = Relationship(back_populates="devices")
    token_families: List["TokenFamily"] = Relationship(back_populates="device")
