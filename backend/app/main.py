from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

import os

# Harden CORS: allow explicit origins, restrict headers, disable LAN regex in production
origins = settings.allowed_origins_list
is_prod = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower() in ("production", "prod")

if origins == ["*"]:
    allow_origins = ["*"] if not is_prod else []
    allow_origin_regex = None
else:
    allow_origins = origins
    if is_prod:
        # Production: explicit origins only, no regex fallback
        allow_origin_regex = None
    else:
        # Dev: allow localhost/127.0.0.1 + LAN private IP for Network/QR code
        allow_origin_regex = (
            r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0"
            r"|10\.\d+\.\d+\.\d+"
            r"|192\.168\.\d+\.\d+"
            r"|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+"
            r")(:\d+)?"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Total-Count"],
    max_age=600,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
