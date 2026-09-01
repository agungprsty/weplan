"""Create superadmin weplansuper@gmail.com

Usage:
  python -m scripts.create_superadmin
  ADMIN_EMAIL=weplansuper@gmail.com ADMIN_PASSWORD=changeme python -m scripts.create_superadmin

Idempotent: if user exists, sets is_superadmin=True and optionally resets password.
"""

import asyncio
import os
import sys

# ensure app import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User


DEFAULT_EMAIL = os.getenv("ADMIN_EMAIL", "kanikahsuper@gmail.com")
DEFAULT_PASSWORD = os.getenv("ADMIN_PASSWORD", "Kanikahsuper1!")
DEFAULT_NAME = os.getenv("ADMIN_NAME", "Kanikah SuperAdmin")


async def main() -> None:
    email = DEFAULT_EMAIL
    password = DEFAULT_PASSWORD
    async with async_session_factory() as session:  # type: AsyncSession
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                full_name=DEFAULT_NAME,
                is_active=True,
                is_superadmin=True,
                provider="email",
                email_verified=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"[seed] created superadmin {email} id={user.id}")
            print(f"[seed] password: {password} (change after first login!)")
        else:
            changed = False
            if not user.is_superadmin:
                user.is_superadmin = True
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            # if hashed_password is None (google user) set password
            if password and os.getenv("ADMIN_RESET_PASSWORD") == "1":
                user.hashed_password = hash_password(password)
                changed = True
            if changed:
                await session.commit()
                await session.refresh(user)
                print(f"[seed] updated superadmin {email} id={user.id}")
            else:
                print(f"[seed] superadmin {email} already exists id={user.id} (no change)")
        # print token hint
        from app.core.security import create_access_token

        token = create_access_token(str(user.id))
        print(f"[seed] test JWT (30m): {token[:40]}...")


if __name__ == "__main__":
    asyncio.run(main())
