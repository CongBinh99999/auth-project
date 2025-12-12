from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.role_permission import RolePermission

if TYPE_CHECKING: 
    from app.models.permission import Permission 
    from app.models.user import User

class Role(SQLModel, table=True): 
    __tablename__="roles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100)
    code: str = Field(max_length=100, unique= True)
    description: Optional[str]
    is_default: bool = Field(default=False)
    is_system: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission,
    )
    users: List["User"] = Relationship(
        back_populates="role"
    )

    

