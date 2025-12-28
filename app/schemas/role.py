from pydantic import BaseModel, ConfigDict, Field, ConfigDict
from typing import Optional 


class RoleBase(BaseModel): 
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=8, max_length=255, description="Name role")
    code: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Z][A-Z0-9_]*$" description="Unique code identifier for the role (e.g., ADMIN, USER, MODERATOR)")
    description: str | None = Field(None, max_length=500, description="Role description")


class RoleCreate(RoleBase): 
    model_config = ConfigDict(from_attributes=True)

    is_default: bool = Field(..., default=False)
    is_system: bool = Field(..., default=False)


class RoleUpdate(BaseModel): 
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(..., min_length=8, max_length=255, description="Name role")
    code: Optional[str] = Field(None, min_length=1, max_length=50, pattern=r"^[A-Z][A-Z0-9_]*$")
    description: Optional[str] = Field(None, max_length=500)
    is_default: Optional[bool] = Field(None)
    is_system: Optional[bool] = Field(None)

class RoleResponse(RoleBase):
    """Schema trả về cho client."""
    id: UUID
    is_default: bool
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class RoleWithPermissions(RoleResponse):
    """Role kèm danh sách permissions."""
    permissions: List["PermissionResponse"] = []


class PermissionBase(BaseModel):
    """Base schema cho Permission."""
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1, max_length=255, description="Permission name")
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        pattern=r"^[a-z][a-z0-9_:]*$",
        description="Permission code (e.g., user:read, user:write)"
    )
    description: Optional[str] = Field(None, max_length=500)
    module: str = Field(..., min_length=1, max_length=100, description="Module name (e.g., user, role)")


class PermissionCreate(PermissionBase):
    """Schema khi tạo Permission mới."""
    pass


class PermissionResponse(PermissionBase):
    """Schema trả về cho client."""
    id: UUID
    created_at: datetime


RoleWithPermissions.model_rebuild()
    