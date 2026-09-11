import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class RolePermission(SQLModel, table=True): 
    __tablename__ = "role_permissions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id")
    permission_id: uuid.UUID = Field(foreign_key="permissions.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
