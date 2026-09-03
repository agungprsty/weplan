import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    # normalisasi email (lower + strip) — best practice cegah duplicate case-sensitive
    normalized_email = data.email.strip().lower()
    existing = await db.execute(select(User).where(User.email == normalized_email))
    if existing.scalar_one_or_none() is not None:
        raise ValueError("Email already registered")

    user = User(
        email=normalized_email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name.strip(),
    )
    db.add(user)
    try:
        await db.flush()
    except Exception as exc:  # race condition: 2 request concurrent lolos check lalu violates unique
        from sqlalchemy.exc import IntegrityError

        if isinstance(exc, IntegrityError):
            raise ValueError("Email already registered") from exc
        raise
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, data: LoginRequest) -> User | None:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not user.hashed_password:
        return None
    if not user.is_active:
        return None
    if not verify_password(data.password, user.hashed_password):
        return None
    return user


def generate_tokens(user_id: str) -> dict:
    return {
        "access_token": create_access_token(subject=user_id),
        "refresh_token": create_refresh_token(subject=user_id),
        "token_type": "bearer",
    }


async def update_user_profile(
    db: AsyncSession, user: User, full_name: str | None, email: str | None
) -> User:
    if email and email != user.email:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Email sudah digunakan")
        user.email = email
    if full_name is not None:
        user.full_name = full_name.strip()
    await db.flush()
    await db.refresh(user)
    return user


async def change_user_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> None:
    if new_password != confirm_password:
        raise ValueError("Konfirmasi password tidak cocok")
    if len(new_password) < 8:
        raise ValueError("Password baru minimal 8 karakter")
    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Password saat ini salah")
    user.hashed_password = hash_password(new_password)
    await db.flush()


def generate_pair_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def reset_password_with_token(
    db: AsyncSession, token: str, new_password: str, confirm_password: str
) -> None:
    from jwt import ExpiredSignatureError, InvalidTokenError

    from app.core.security import hash_password, verify_token

    if new_password != confirm_password:
        raise ValueError("Konfirmasi password tidak cocok")
    if len(new_password) < 8:
        raise ValueError("Password baru minimal 8 karakter")

    try:
        payload = verify_token(token)
        if payload.get("type") != "reset":
            raise ValueError("Token tidak valid")  # noqa: TRY301
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token tidak valid")
    except ExpiredSignatureError as exc:
        raise ValueError(
            "Token reset sudah kadaluarsa, silakan minta link baru"
        ) from exc
    except InvalidTokenError as exc:
        raise ValueError("Token tidak valid") from exc

    import uuid

    user = await db.get(User, uuid.UUID(str(user_id)))
    if user is None or not user.is_active:
        raise ValueError("User tidak ditemukan")

    user.hashed_password = hash_password(new_password)
    await db.flush()


async def authenticate_google_user(db: AsyncSession, id_token: str) -> User:
    """Verifikasi Google ID token (GIS) dan cari/buat user. Stateless, tanpa simpan token Google."""  # noqa: E501
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    from app.core.config import settings

    if not settings.GOOGLE_CLIENT_ID:
        raise ValueError("Google login belum dikonfigurasi (GOOGLE_CLIENT_ID kosong)")

    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise ValueError(f"Google token tidak valid: {e}") from e

    # validasi dasar
    if idinfo.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise ValueError("Google token audience tidak cocok")
    if not idinfo.get("email") or not idinfo.get("email_verified"):
        raise ValueError("Email Google belum terverifikasi")

    google_id = idinfo.get("sub")
    email = idinfo.get("email")
    full_name = idinfo.get("name") or email.split("@")[0]
    avatar_url = idinfo.get("picture")
    email_verified = bool(idinfo.get("email_verified"))

    # cari by google_id dulu, lalu email
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()
    if user is not None:
        # update avatar/name jika berubah
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
        if email_verified:
            user.email_verified = True
        await db.flush()
        await db.refresh(user)
        return user

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        # linking: email sudah ada (daftar manual) → hubungkan google_id
        if user.google_id and user.google_id != google_id:
            raise ValueError("Email sudah terhubung dengan akun Google lain")
        user.google_id = google_id
        user.provider = "google"
        user.avatar_url = avatar_url
        user.email_verified = True
        await db.flush()
        await db.refresh(user)
        return user

    # buat user baru tanpa password
    user = User(
        email=email,
        hashed_password=None,
        full_name=full_name,
        google_id=google_id,
        provider="google",
        avatar_url=avatar_url,
        email_verified=email_verified,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
