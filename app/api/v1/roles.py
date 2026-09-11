from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import RequireAdmin
from app.schemas.role import PermissionResponse, RoleCreate, RoleResponse, RoleUpdate
from app.services.role_service import RoleServiceDep

router = APIRouter(
    prefix="/roles",
    tags=["Roles"], 
    dependencies=[RequireAdmin]
)

@router.get(
    "/",
    response_model=list[RoleResponse],
    summary="Lấy tất cả role"
)
async def get_all_role(
    role_service: RoleServiceDep
) -> list[RoleResponse]: 
    return await role_service.get_all_role()


@router.get(
    "/{role_id}",
    response_model=RoleResponse, 
    summary="Lấy một role cụ thể"
)
async def get_role(
    role_id: UUID, 
    role_service: RoleServiceDep
) -> RoleResponse: 
    return await role_service.get_role(role_id)


@router.post(
    "/", 
    response_model=RoleResponse, 
    summary="Tạo role"
) 
async def create_role(
    data: RoleCreate, 
    role_service: RoleServiceDep
) -> RoleResponse: 
    return await role_service.create_role(
        code=data.code, 
        name=data.name, 
        description=data.description,
        is_default=data.is_default,
        is_system=data.is_system
    )


@router.patch(
    "/{role_id}",
    response_model=RoleResponse, 
    summary="cập nhật role"
)
async def update_role(
    role_id: UUID,
    update_data: RoleUpdate, 
    role_service: RoleServiceDep
) -> RoleResponse: 
    return await role_service.update_role(
        role_id=role_id, 
        code=update_data.code, 
        name=update_data.name, 
        description=update_data.description,
        is_default=update_data.is_default,
        is_system=update_data.is_system
    )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa role"
)
async def delete_role(
    role_id: UUID, 
    role_service: RoleServiceDep
) -> None: 
    return await role_service.delete_role(role_id)


@router.get(
    "/{role_id}/permissions",
    response_model=list[PermissionResponse],
    summary="Lấy tất cả quyền của role"
)
async def get_role_permissions(
    role_id: UUID, 
    role_service: RoleServiceDep
) -> list[PermissionResponse]:
    return await role_service.get_role_permissions(role_id)


@router.post(
    "/{role_id}/permissions/{permission_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Gán quyền cho role"
)
async def assign_permission(
    role_id: UUID, 
    permission_id: UUID, 
    role_service: RoleServiceDep
) -> None: 
    await role_service.assign_permission(role_id, permission_id)


@router.delete(
    "/{role_id}/permissions/{permission_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Gỡ quyền cho role"
)
async def remove_permission(
    role_id: UUID, 
    permission_id: UUID, 
    role_service: RoleServiceDep
) -> None: 
    await role_service.remove_permission(role_id, permission_id)

    