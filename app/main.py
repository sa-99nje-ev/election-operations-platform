import os
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from app.routers import results


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    print(f"🚀 Connecting to Redis at {redis_host}:{redis_port}")

    app.state.redis_pool = await create_pool(
        RedisSettings(
            host=redis_host,
            port=redis_port
        )
    )

    print("✅ Redis connection pool initialized")

    try:
        yield
    finally:
        await app.state.redis_pool.close(close_connection_pool=True)
        print("✅ Redis connection pool closed")


app = FastAPI(
    title="Election Operations Platform",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "redis_connected": bool(
            getattr(app.state, "redis_pool", None)
        )
    }


# Mount results router
app.include_router(results.router)
