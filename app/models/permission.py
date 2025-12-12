import uuid
from datetime import datetime, timezone 
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import SQLModel, Field, Relationship
from app.models.role_permission import RolePermission

if TYPE_CHECKING: 
    from app.models.role import Role

class Permission(SQLModel, table=True): 
    __tablename__="permissions" 
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100)
    code: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default=None)
    module: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    roles: list["Role"] = Relationship(
        back_populates="permissions", 
        link_model=RolePermission, 
    )


