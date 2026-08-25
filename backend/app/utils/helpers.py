from datetime import UTC, date, datetime


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def format_date(d: date | None) -> str | None:
    if d is None:
        return None
    return d.isoformat()
