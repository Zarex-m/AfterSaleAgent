from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User, UserRole
from app.schemas.auth import UserRegisterRequest


async def get_user_by_email(db:AsyncSession,email:str)->User:
    result=await db.execute(select(User).where(User.email==email))
    return result.scalar_one_or_none()

#注册用户
async def register_user(
    db:AsyncSession,
    data:UserRegisterRequest,
)->User:
    existing_user=await get_user_by_email(db, data.email)
    if existing_user:
        raise ValueError("Email already registered")
    
    hashed_password=hash_password(data.password)
    new_user=User(
        email=data.email,
        hashed_password=hashed_password,
        role=UserRole.AGENT.value,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

#验证用户邮箱和密码是否正确，如果正确返回用户对象，否则返回None
async def authenticate_user(
    db:AsyncSession,
    email:str,
    password:str,
)->User:
    user=await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

#登录用户，验证成功后返回JWT token
async def login_user(
    db:AsyncSession,
    email:str,
    password:str,
)->str:
    user=await authenticate_user(db, email, password)
    if not user:
        raise ValueError("Invalid email or password")
    
    access_token=create_access_token(subject=str(user.id), extra_claims={"role": user.role})
    return access_token
