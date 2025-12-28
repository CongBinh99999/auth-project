from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Any
from datetime import datetime
import uuid
from typing_extensions import Self


class LoginRequest(BaseModel): # yêu cầu login
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseModel): 
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
 

class RefreshTokenRequest(BaseModel): # yêu cầu để cấp lại token 
    refresh_token:str 


class RegisterRequest(BaseModel): # yêu cầu đăng ký 
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    comfirm_password: str = Field(..., min_length=8, max_length=255)

    @model_validator(mode='before')
    @classmethod
    def pre_process_data(cls, data: Any) -> Any: 
        # Lúc này 'data' thường là Dict (dữ liệu thô)
        if isinstance(data, dict): 
            if "email" in data: 
                data["email"] = data["email"].strip().lower()
            if "password" in data: 
                data["password"] = data["password"].strip()
            if "comfirm_password" in data:
                data["comfirm_password"] = data["comfirm_password"].strip()
        return data 

    @model_validator(mode='after')
    def validate_password(self)-> Self:
        if self.password != self.comfirm_password: 
            raise ValueError("Mật khẩu không khớp với nhau")
        return self 


from app.utils.constants import TokenType


class TokenPayload(BaseModel): # khi tạo JWT phải tuân theo
    sub: uuid.UUID
    jti: uuid.UUID
    type: TokenType = TokenType.ACCESS
    family_id: Optional[uuid.UUID]
    iat: datetime   
    exp: datetime



RegisterRequest(
    email="  TEST@GMAIL.COM ",
    password="12345678",
    comfirm_password="12345678"
)