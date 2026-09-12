from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import ActiveUser
from app.schemas.device import DeviceListResponse, DeviceResponse, DeviceUpdate
from app.services.device_service import DeviceServiceDep

router = APIRouter(
    prefix="/devices", 
    tags=["Devices"],
    # dependencies=[Depends(HTTPBearer())] 
)


@router.get(
    "/",
    response_model=DeviceListResponse,
    summary="lấy tất cả thiết bị của user"
)
async def get_my_devices(
    user: ActiveUser,
    device_service: DeviceServiceDep
) -> DeviceListResponse: 
    devices =  await device_service.get_user_devices(user_id=user.id)

    return DeviceListResponse(
        devices=devices,
        total_count=len(devices)
    )


@router.get(
    "/{device_id}", 
    response_model=DeviceResponse,
    summary="Lấy thông tin một thiết bị"
)
async def get_device(
    device_id: UUID,
    user: ActiveUser, 
    device_service: DeviceServiceDep
) -> DeviceResponse: 
    return await device_service.get_device_by_id(device_id, user.id)


@router.patch(
    "/{device_id}", 
    response_model=DeviceResponse, 
    summary="cập nhật thông tin thiết bị"
)
async def update_device(
    user: ActiveUser, 
    device_service: DeviceServiceDep, 
    device_id: UUID, 
    data: DeviceUpdate 
) -> DeviceResponse: 
    
    return await device_service.update(
        user_id=user.id,
        device_id=device_id,
        update_schema=data
    )


@router.post(
    "/{device_id}/trust", 
    response_model=DeviceResponse,
    summary="Đánh dấu thiết bị là trusted"
)
async def trust_device(
    device_id: UUID,
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    return await device_service.trust_device(device_id, user.id)


@router.delete(
    "/{device_id}/trust", 
    response_model=DeviceResponse,
    summary="Gỡ trust khỏi thiết bị"
)
async def untrust_device(
    device_id: UUID,
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    return await device_service.untrust_device(device_id, user.id)


@router.post(
    "/{device_id}/block",
    response_model=DeviceResponse,
    summary="Chặn thiết bị"
)
async def block_device(
    device_id: UUID,
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    """Chặn thiết bị. Lần đăng nhập sau từ thiết bị này sẽ bị từ chối."""
    return await device_service.block_device(device_id, user.id)


@router.delete(
    "/{device_id}/block",
    response_model=DeviceResponse,
    summary="Gỡ chặn thiết bị"
)
async def unblock_device(
    device_id: UUID,
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    return await device_service.unblock_device(device_id, user.id)


@router.delete(
    "/{device_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thiết bị"
)
async def remove_device(
    device_id: UUID,
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    await device_service.remove_device(device_id, user.id)


@router.delete(
    "/", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa tất cả thiết bị"
)
async def remove_all_devices(
    user: ActiveUser,
    device_service: DeviceServiceDep
):
    await device_service.remove_all_devices(user.id)

    

    


