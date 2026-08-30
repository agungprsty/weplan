import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.wedding import Wedding
from app.models.wedding_user import WeddingUser

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception

    user = await db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_current_wedding(
    wedding_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Wedding:
    stmt = select(WeddingUser).where(
        WeddingUser.wedding_id == wedding_id,
        WeddingUser.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    wedding_user = result.scalar_one_or_none()

    if wedding_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this wedding",
        )

    # pakai selectinload(plan) agar tidak MissingGreenlet saat serialisasi response (async lazy load)
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Wedding).options(selectinload(Wedding.plan)).where(Wedding.id == wedding_id)
    )
    wedding = result.scalar_one_or_none()
    if wedding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wedding not found",
        )
    return wedding


async def get_current_superadmin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
