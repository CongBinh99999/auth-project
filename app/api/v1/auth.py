from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import (
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.schemas.email_verification import (
    EmailVerifyRequest,
    EmailVerifyResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
)
from app.schemas.password_reset import (
    PasswordResetConfirm,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.services.auth_service import AuthServiceDep
from app.services.email_verification_service import EmailVerificationServiceDep
from app.services.password_reset_service import PasswordResetServiceDep

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register", 
    response_model=RegisterResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Đăng ký tài khoản"
)
async def register(
    data: RegisterRequest, 
    auth_service: AuthServiceDep,
    background_tasks: BackgroundTasks
) -> RegisterResponse: 
    
    user = await auth_service.register(
        email=data.email, 
        full_name=data.full_name,
        password=data.password,
        background_tasks=background_tasks
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
        await auth_service.logout_all(user_id=payload.sub)

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


@router.get(
    "/verify-email",
    response_model=EmailVerifyResponse,
    summary="Xác thực email"
)
async def verify_email_link(
    verification_service: EmailVerificationServiceDep,
    token: str = Query(..., min_length=1, description="Token xác thực email")
) -> EmailVerifyResponse:
    """Xác thực email qua link trong mail (email_service gửi đúng URL này)."""

    await verification_service.verify_email(token)

    return EmailVerifyResponse(
        message="Xác thực email thành công",
        verified=True
    )


@router.post(
    "/verify-email",
    response_model=EmailVerifyResponse,
    summary="Xác thực email"
)
async def verify_email(
    data: EmailVerifyRequest,
    verification_service: EmailVerificationServiceDep
) -> EmailVerifyResponse:
    """Xác thực email bằng token, cho client tự gọi API."""

    await verification_service.verify_email(data.token)

    return EmailVerifyResponse(
        message="Xác thực email thành công",
        verified=True
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    summary="Gửi lại email xác thực"
)
async def resend_verification(
    data: ResendVerificationRequest,
    auth_service: AuthServiceDep,
    background_tasks: BackgroundTasks
) -> ResendVerificationResponse:
    """Gửi lại link xác thực. Trả lời giống nhau dù email có tồn tại hay không."""

    await auth_service.resend_verification(data.email, background_tasks)

    return ResendVerificationResponse(
        message="Nếu email tồn tại và chưa xác thực, link mới đã được gửi",
        success=True
    )


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    summary="Yêu cầu đặt lại mật khẩu"
)
async def forgot_password(
    data: PasswordResetRequest,
    auth_service: AuthServiceDep,
    background_tasks: BackgroundTasks
) -> PasswordResetResponse:
    """Gửi link đặt lại mật khẩu. Trả lời giống nhau dù email có tồn tại hay không."""

    await auth_service.request_password_reset(data.email, background_tasks)

    return PasswordResetResponse(
        message="Nếu email tồn tại, link đặt lại mật khẩu đã được gửi",
        success=True
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetConfirmResponse,
    summary="Đặt lại mật khẩu"
)
async def reset_password(
    data: PasswordResetConfirm,
    reset_service: PasswordResetServiceDep
) -> PasswordResetConfirmResponse:
    """Đặt mật khẩu mới bằng token từ email, đồng thời thu hồi mọi session cũ."""

    await reset_service.reset_password(data.token, data.new_password)

    return PasswordResetConfirmResponse(
        message="Đặt lại mật khẩu thành công",
        success=True
    )
