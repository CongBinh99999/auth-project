from fastapi import APIRouter, Depends, Query, Request, status
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
from app.services.auth_service import AuthServiceDep
from app.services.email_verification_service import EmailVerificationServiceDep

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
    auth_service: AuthServiceDep
) -> ResendVerificationResponse:
    """Gửi lại link xác thực. Trả lời giống nhau dù email có tồn tại hay không."""

    await auth_service.resend_verification(data.email)

    return ResendVerificationResponse(
        message="Nếu email tồn tại và chưa xác thực, link mới đã được gửi",
        success=True
    )
