from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import login_user, register_user
from app.api.dependencies import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        user=await register_user(db, data)
    except ValueError as exc:
        if str(exc)=="Email already registered":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")from exc
        raise
    return UserResponse.model_validate(user)

@router.post("/login",response_model=TokenResponse)
async def login(
    data:UserLoginRequest,
    db:AsyncSession=Depends(get_db),
)->TokenResponse:
    access_token=await login_user(db, data.email, data.password)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)