from datetime import UTC, datetime

from app.models.wedding import Wedding


def is_premium_wedding(wedding: Wedding) -> bool:
    """Single source of truth for premium check.

    Premium = plan.slug == 'premium' AND plan_expires_at > now(UTC).
    Handles naive UTC timestamps stored in DB (utcnow naive) by comparing naive.
    Falls back to plan_id check if plan relationship not loaded.
    """
    if wedding.plan_expires_at is None:
        return False
    # DB stores naive UTC (utcnow naive). Compare naive.
    now = datetime.now(UTC).replace(tzinfo=None)
    # Prefer slug check if plan loaded
    if wedding.plan is not None:
        return wedding.plan.slug == "premium" and wedding.plan_expires_at > now
    # Fallback: if plan not loaded but plan_id exists, assume premium if not expired
    # (kept for backward compat, but caller should eager-load plan)
    return wedding.plan_id is not None and wedding.plan_expires_at > now


def get_active_plan_slug(wedding: Wedding) -> str | None:
    if wedding.plan is not None:
        return wedding.plan.slug
    return None
