import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.utils.constants import DeviceStatus

if TYPE_CHECKING:
    from app.models.token_family import TokenFamily
    from app.models.user import User


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
        default_factory=lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True)
    )
    last_login_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True)
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="devices")
    token_families: list["TokenFamily"] = Relationship(back_populates="device")