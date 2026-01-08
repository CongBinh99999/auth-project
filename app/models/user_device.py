import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum as SAEnum, Column

from app.utils.constants import DeviceStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.token_family import TokenFamily


class UserDevice(SQLModel, table=True):
    __tablename__ = "user_devices"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    device_name: Optional[str] = Field(default=None, max_length=255)
    device_type: Optional[str] = Field(default=None, max_length=50)
    browser: Optional[str] = Field(default=None, max_length=100)
    os: Optional[str] = Field(default=None, max_length=100)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    fingerprint: Optional[str] = Field(default=None, max_length=255)
    
    status: DeviceStatus = Field(
        default=DeviceStatus.ACTIVE,
        sa_column=Column(
            SAEnum(
                DeviceStatus,
                name="device_status",
                create_type=False, 
                values_callable=lambda x: [e.value for e in x]
            ),
            nullable=False,
            default="active"
        )
    )
    
    is_trusted: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_type=DateTime(timezone=True)
    )
    last_login_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_type=DateTime(timezone=True)
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="devices")
    token_families: List["TokenFamily"] = Relationship(back_populates="device")