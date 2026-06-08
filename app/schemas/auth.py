"""
定义登录和注册相关的响应模型
"""
from pydantic import BaseModel, EmailStr,Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password:str=Field(min_length=8, max_length=128)
    
class UserLoginRequest(BaseModel):
    email: EmailStr
    password:str=Field(min_length=8, max_length=128)
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id:int
    email: EmailStr
    role:str
    is_active:bool
    
    model_config={"from_attributes": True}
