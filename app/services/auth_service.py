"""Auth Service - Authentication orchestration.

Orchestration service điều phối toàn bộ quy trình authentication
bao gồm Register, Login, Logout, và Token Refresh.
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends

from app.core.exceptions import (
    EmailExistsException,
    InvalidCredentialsException,
    RoleNotFoundException,
    TooManyLoginAttemptsException,
    UserInactiveException,
    UserNotVerifiedException,
)
from app.core.security import hash_password, verify_password
from app.models.token_blacklist import TokenType
from app.models.user import User
from app.repositories.role_repository import RoleRepoDep, RoleRepository
from app.repositories.user_repository import UserRepoDep, UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse
from app.services.device_service import DeviceService, DeviceServiceDep
from app.services.email_service import EmailService, EmailServiceDep
from app.services.email_verification_service import (
    EmailVerificationService,
    EmailVerificationServiceDep,
)
from app.services.login_attempt_service import (
    LoginAttemptService,
    LoginAttemptServiceDep,
)
from app.services.token_family_service import TokenFamilyService, TokenFamilyServiceDep
from app.services.token_service import TokenBlacklistServiceDep, TokenService


class AuthService:
    """Orchestration service cho Authentication.
    
    Đây là service chính điều phối toàn bộ quy trình xác thực,
    kết hợp nhiều repositories và services khác.
    
    Cung cấp các chức năng:
    - Register: Đăng ký tài khoản mới
    - Login: Đăng nhập và cấp tokens
    - Logout: Đăng xuất và vô hiệu hóa tokens
    - Refresh Token: Làm mới access token
    - Logout All: Đăng xuất tất cả thiết bị
    
    Attributes:
        user_repo: Repository để thao tác với User entity.
        role_repo: Repository để lấy default role.
        token_service: Service quản lý JWT tokens.
        token_family_service: Service quản lý refresh token rotation.
        login_attempt_service: Service quản lý rate limiting.
        email_verification_service: Service xác thực email.
        device_service: Service quản lý devices (optional).
    """

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        token_service: TokenService,
        token_family_service: TokenFamilyService,
        login_attempt_service: LoginAttemptService,
        email_verification_service: EmailVerificationService,
        email_service: EmailService,
        device_service: DeviceService | None = None
    ): 
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.token_service = token_service
        self.token_family_service = token_family_service
        self.login_attempt_service = login_attempt_service
        self.email_verification_service = email_verification_service
        self.email_service = email_service
        self.device_service = device_service


    async def register(
        self, 
        email: str, 
        password: str, 
        full_name: str | None = None
    ) -> UserResponse:
        """Đăng ký tài khoản mới.
        
        Flow:
        1. Kiểm tra email chưa tồn tại
        2. Lấy default role
        3. Hash password
        4. Tạo user mới
        5. Tạo email verification token
        
        Args:
            email: Email đăng ký.
            password: Mật khẩu (plain text, sẽ được hash).
            full_name: Tên đầy đủ (optional).
            
        Returns:
            UserResponse chứa thông tin user mới.
            
        Raises:
            EmailExistsException: Email đã được sử dụng.
            RoleNotFoundException: Không tìm thấy default role.
        """
        user = await self.user_repo.get_by_email(email)
        if user: 
            raise EmailExistsException()
        
        default_role = await self.role_repo.get_default_role()
        if not default_role: 
            raise RoleNotFoundException()
        
        hashed_password = hash_password(password)

        new_user = await self.user_repo.create(
            email=email, 
            hashed_password=hashed_password,
            full_name=full_name,
            role_id=default_role.id
        )

        verification_token = await self.email_verification_service.create_verification_token(
            user_id=new_user.id,
            email=new_user.email
        )
        
        # Gửi email xác thực
        self.email_service.send_verification_email(
            to_email=new_user.email,
            token=verification_token
        )

        return UserResponse.model_validate(new_user)


    async def authenticate_user(self, email: str, password: str) -> User:
        """Xác thực user (internal helper).
        
        Kiểm tra credentials và trạng thái của user.
        
        Args:
            email: Email đăng nhập.
            password: Mật khẩu (plain text).
            
        Returns:
            User entity nếu xác thực thành công.
            
        Raises:
            InvalidCredentialsException: Email hoặc password sai.
            UserInactiveException: Tài khoản bị khóa.
            UserNotVerifiedException: Email chưa xác thực.
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsException()
        
        if not verify_password(password, user.hashed_password): 
            raise InvalidCredentialsException()
        
        if not user.is_active: 
            raise UserInactiveException()

        if not user.is_verified:
            raise UserNotVerifiedException()

        return user
    

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str | None = None
    ) -> TokenResponse:
        """Đăng nhập và cấp tokens."""
        
        if await self.login_attempt_service.is_blocked(email, ip_address):
            raise TooManyLoginAttemptsException()

        try:
            user = await self.authenticate_user(email, password)
        except InvalidCredentialsException:
            await self.login_attempt_service.record_attempt(
                email, ip_address, False, None, user_agent, "invalid_credentials"
            )
            raise
        except UserInactiveException:
            await self.login_attempt_service.record_attempt(
                email, ip_address, False, None, user_agent, "user_inactive"
            )
            raise
        except UserNotVerifiedException:
            await self.login_attempt_service.record_attempt(
                email, ip_address, False, None, user_agent, "user_not_verified"
            )
            raise

        await self.login_attempt_service.record_attempt(
            email, ip_address, True, user.id, user_agent
        )
        await self.login_attempt_service.clear_attempts_on_success(email, ip_address)

        device = None
        if self.device_service:
            device = await self.device_service.register_device(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent
            )

        refresh_jti = str(uuid4())
        
        token_family = await self.token_family_service.create_family(
            user_id=user.id,
            initial_jti=refresh_jti,  
            device_id=device.id if device else None
        )

        await self.user_repo.update(
            user,
            last_login_at=datetime.now(UTC)
        )

        if device:
            await self.device_service.update_device_last_login(device)

        return self.token_service.create_pair_token(
            user_id=user.id, 
            family_id=token_family.id,
            refresh_jti=refresh_jti 
        )


    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Làm mới access token."""
        
        family, _ = await self.token_family_service.validate_refresh_token(refresh_token)

        new_jti = str(uuid4())
        
        await self.token_family_service.rotate_token(family, new_jti)

        await self.token_family_service.update_last_used(family)

        return self.token_service.create_pair_token(
            user_id=family.user_id,
            family_id=family.id,
            refresh_jti=new_jti 
        )


    async def logout(self, access_token: str, refresh_token: str | None = None) -> None:
        """Đăng xuất khỏi session hiện tại.
        
        Flow:
        1. Blacklist access token
        2. Nếu có refresh token → revoke token family
        
        Args:
            access_token: Access token cần blacklist.
            refresh_token: Refresh token để revoke family (optional).
        """
        payload = self.token_service.decode_token(access_token)
        await self.token_service.blacklist_token(
            jti=str(payload.jti),
            token_type=TokenType.ACCESS,
            user_id=payload.sub,
            expires_at=payload.exp
        )
        if refresh_token:
            family, _ = await self.token_family_service.validate_refresh_token(refresh_token)
            await self.token_family_service.revoke_family(family.id)


    async def logout_all(self, user_id: UUID) -> int:
        """Đăng xuất khỏi tất cả thiết bị.
        
        Revoke tất cả token families của user.
        
        Args:
            user_id: UUID của user.
            
        Returns:
            Số lượng sessions đã đăng xuất.
        """
        return await self.token_family_service.revoke_all_user_sessions(user_id)


def get_auth_service(
    user_repo: UserRepoDep, 
    role_repo: RoleRepoDep,
    token_service: TokenBlacklistServiceDep,
    token_family_service: TokenFamilyServiceDep, 
    login_attempt_service: LoginAttemptServiceDep,
    email_verification_service: EmailVerificationServiceDep,
    email_service: EmailServiceDep,
    device_service: DeviceServiceDep
) -> AuthService:
    """Dependency injection factory cho AuthService."""
    return AuthService(
        user_repo, 
        role_repo,
        token_service,
        token_family_service, 
        login_attempt_service,
        email_verification_service,
        email_service,
        device_service
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
