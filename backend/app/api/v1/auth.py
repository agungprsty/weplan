from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_token
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    Token,
)
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.services import auth as auth_service

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    try:
        user = await auth_service.register_user(db, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return user


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    try:
        updated = await auth_service.update_user_profile(
            db, current_user, data.full_name, data.email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e  # noqa: E501
    return updated


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e  # noqa: E501
    return {"message": "Password berhasil diubah"}


@router.post("/refresh", response_model=Token)
async def refresh(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Stateless refresh: verifikasi refresh_token (type=refresh)
    lalu terbitkan pasangan baru. Tidak perlu DB, kompatibel dengan
    token lama. Background retry tanpa ganggu user."""
    import uuid

    try:
        payload = verify_token(data.refresh_token)
        token_type = payload.get("type")
        user_id = payload.get("sub")
        if token_type != "refresh" or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token tidak valid",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired, silakan login kembali",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await db.get(User, uuid.UUID(str(user_id)))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan atau tidak aktif",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = auth_service.generate_tokens(str(user.id))
    return Token(**tokens)


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Selalu 200 untuk hindari enumerasi email. Jika email ada, buat JWT reset 15m dan log link."""  # noqa: E501
    from sqlalchemy import select

    from app.core.security import create_reset_token

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user is not None:
        token = create_reset_token(str(user.id))
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        # best-praktis minimal: log ke console, ganti dengan kirim email via SMTP di prod  # noqa: E501
        import logging

        logging.getLogger("kanikah.auth").info(
            "Reset link for %s: %s", user.email, reset_link
        )  # noqa: E501
        print(f"[kanikah] Reset link for {user.email}: {reset_link}")
    return {"message": "Jika email terdaftar, link reset telah dikirim"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    try:
        await auth_service.reset_password_with_token(
            db, data.token, data.new_password, data.confirm_password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e  # noqa: E501
    return {"message": "Password berhasil direset, silakan login"}


@router.post("/google", response_model=Token)
async def google_login(
    data: GoogleLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Login/register via Google ID token (GIS). Stateless, minimal perubahan."""
    try:
        user = await auth_service.authenticate_google_user(db, data.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e  # noqa: E501
    tokens = auth_service.generate_tokens(str(user.id))
    return Token(**tokens)
