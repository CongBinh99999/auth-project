from fastapi import APIRouter, Request, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID

from app.core.dependencies import ActiveUser, oauth2_scheme
from app.services.auth_service import AuthServiceDep 

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    RefreshTokenRequest, 
    LogoutRequest,
    LogoutResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register", 
    response_model=RegisterResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Đăng ký tài khoản"
)
async def register(
    data: RegisterRequest, 
    auth_service: AuthServiceDep
) -> RegisterResponse: 
    
    user = await auth_service.register(
        email=data.email, 
        full_name=data.full_name,
        password=data.password
    )

    return RegisterResponse(
        message="Đăng ký thành công", 
        user_id= user.id, 
        email=user.email, 
        requires_verification=True
    )


@router.post(
    "/login", 
    response_model=TokenResponse, 
    summary="Đăng nhập"
)
async def login (
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    auth_service: AuthServiceDep = None
) -> TokenResponse: 
    
    host = request.client.host if request.client else "unknow"
    user_agent = request.headers.get("user-agent") 
    return await auth_service.login(
        email=form_data.username,
        password=form_data.password, 
        ip_address=host,
        user_agent=user_agent
    )


@router.post(
    "/refresh", 
    response_model=TokenResponse,
    summary="Làm mới Token"
)
async def refresh(
    data: RefreshTokenRequest, 
    auth_service: AuthServiceDep
) -> TokenResponse: 
    return await auth_service.refresh_token(refresh_token=data.refresh_token)


@router.post(
    "/logout", 
    response_model=LogoutResponse, 
    summary="Đăng xuất"
)
async def logout(
    data: LogoutRequest,
    auth_service: AuthServiceDep
) -> LogoutResponse: 
    """Đăng xuất - lấy token từ request body."""
    
    await auth_service.logout(
        access_token=data.access_token,
        refresh_token=data.refresh_token
    )
    
    if data.logout_all_devices:
        payload = auth_service.token_service.decode_token(data.access_token)
        await auth_service.logout_all(user_id=UUID(payload.sub))

    return LogoutResponse(
        message="Đăng xuất thành công", 
        success=True
    )


@router.post(
    "/logout-all",
    response_model=LogoutResponse,
    summary="Đăng xuất khỏi tất cả thiết bị"
)
async def logout_all(
    data: LogoutRequest, 
    auth_service: AuthServiceDep
) -> LogoutResponse: 
    """Đăng xuất tất cả - lấy token từ request body."""
    
    payload = auth_service.token_service.decode_token(data.access_token)
    count = await auth_service.logout_all(payload.sub)

    return LogoutResponse(
        message=f"Đã đăng xuất khỏi {count} thiết bị",
        success=True
    )