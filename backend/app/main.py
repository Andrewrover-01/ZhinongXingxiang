from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.cache import close_redis
from app.core.config import settings
from app.core.database import create_tables
from app.routers.auth import router as auth_router
from app.routers.farmland import router as farmland_router
from app.routers.upload import router as upload_router
from app.routers.users import router as users_router
from app.routers.knowledge import router as knowledge_router
from app.routers.ai_doctor import router as ai_doctor_router
from app.routers.policy import router as policy_router


from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.cache import close_redis
from app.core.config import settings
from app.core.database import create_tables
from app.routers.auth import router as auth_router
from app.routers.farmland import router as farmland_router
from app.routers.upload import router as upload_router
from app.routers.users import router as users_router
from app.routers.knowledge import router as knowledge_router
from app.routers.ai_doctor import router as ai_doctor_router
from app.routers.policy import router as policy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    # Auto-create tables for SQLite / development
    create_tables()

    # Reset sse_starlette's AppStatus.should_exit_event so it is always
    # created inside the current event loop.  Without this, the module-level
    # anyio.Event singleton can be bound to a *stale* event loop (e.g. after a
    # hot-reload or in test environments where each TestClient spawns its own
    # loop), causing sse_starlette's listen_for_exit_signal task to raise
    # "RuntimeError: ... is bound to a different event loop" which then
    # propagates as an ExceptionGroup out of the anyio task group.
    try:
        from sse_starlette.sse import AppStatus  # type: ignore
        AppStatus.should_exit_event = None
    except ImportError:  # pragma: no cover
        pass

    yield
    # Gracefully close the Redis connection pool on shutdown
    await close_redis()


app = FastAPI(
    title="智农兴乡 API",
    description="基于 RAG 的智慧农业全栈平台后端接口",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(farmland_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(ai_doctor_router, prefix="/api/v1")
app.include_router(policy_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "欢迎使用《智农兴乡》API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
