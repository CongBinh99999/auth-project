from fastapi import APIRouter, status

from app.core.dependencies import ActiveUser
from app.services.user_service import UserServiceDep
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordChange
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy profile của User"
)
async def get_my_profile(
    user: ActiveUser
) -> UserResponse: 
    
    return user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Cập nhật profile"
)
async def update_my_profile(
    data: UserUpdate, 
    user: ActiveUser,
    user_service: UserServiceDep
) -> UserResponse: 
    return await user_service.update_user_profile(
        user_id=user.id, 
        email=data.email, 
        full_name=data.full_name
    )


@router.patch(
    "/me/password", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Cập nhật mật khẩu"
)
async def change_password(
    data: PasswordChange, 
    user: ActiveUser,
    user_service: UserServiceDep
) -> None: 
    await user_service.change_password(
        user=user,
        old_password=data.old_password, 
        new_password=data.new_password
    )