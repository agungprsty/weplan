from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine


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

# Harden CORS: support multiple origins from env and fallback regex for localhost/127.0.0.1 any port
origins = settings.allowed_origins_list
# if single wildcard configured, allow all
if origins == ["*"]:
    allow_origins = ["*"]
    allow_origin_regex = None
else:
    allow_origins = origins
    # juga izinkan localhost/127.0.0.1 + 0.0.0.0 + LAN private IP (172.16-31.x, 192.168.x, 10.x)
    # dengan port berapa pun (http/https) — untuk dev via Network/QR code
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
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
