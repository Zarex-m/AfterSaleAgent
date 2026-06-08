from datetime import datetime, timedelta,timezone
from typing import Any

import jwt
from passlib.context import CryptContext   

from app.core.config import settings

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

#签名算法
ALGORITHM="HS256"

#生成加密密码
def hash_password(password:str)->str:
    return pwd_context.hash(password)

#验证密码，palint_password是用户输入的密码，hashed_password是数据库中存储的加密密码
def verify_password(plain_password:str, hashed_password:str)->bool:
    return pwd_context.verify(plain_password, hashed_password)

#生成JWT token
def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)