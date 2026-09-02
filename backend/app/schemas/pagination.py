from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    pages: int


def pages_calc(total: int, limit: int) -> int:
    return (total + limit - 1) // limit if limit else 0
