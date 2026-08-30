from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.services import auth as auth_service

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        user = await auth_service.register_user(db, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await auth_service.authenticate_user(db, data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = auth_service.generate_tokens(str(user.id))
    return Token(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        updated = await auth_service.update_user_profile(
            db, current_user, data.full_name, data.email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await auth_service.change_user_password(
            db,
            current_user,
            data.current_password,
            data.new_password,
            data.confirm_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Password berhasil diubah"}
