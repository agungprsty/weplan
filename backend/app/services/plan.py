import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


async def list_active_plans(db: AsyncSession) -> list[Plan]:
    result = await db.execute(select(Plan).where(Plan.is_active))
    return list(result.scalars().all())


async def get_plan_by_id(db: AsyncSession, plan_id: uuid.UUID) -> Plan | None:
    return await db.get(Plan, plan_id)


async def get_plan_by_slug(db: AsyncSession, slug: str) -> Plan | None:
    result = await db.execute(select(Plan).where(Plan.slug == slug))
    return result.scalar_one_or_none()
