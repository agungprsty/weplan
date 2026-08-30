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
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none() is not None:
        raise ValueError("Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, data: LoginRequest) -> User | None:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.hashed_password):
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
