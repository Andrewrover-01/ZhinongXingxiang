import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

_log = logging.getLogger(__name__)

from app.core.cache import close_redis
from app.core.config import settings
from app.core.database import create_tables
from app.core.limiter import limiter  # noqa: F401 — re-exported for convenience
from app.rag.vector_store import get_vector_store
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

    # Pre-warm the VectorStore so the embedding model (ONNX, ~79 MB) is
    # downloaded and loaded at startup rather than blocking the first user
    # query.  This avoids an unexpected long delay (or timeout) on the first
    # request after the knowledge base has been ingested.
    try:
        await asyncio.get_event_loop().run_in_executor(None, get_vector_store)
        _log.info("VectorStore pre-warmed successfully.")
    except Exception as exc:  # noqa: BLE001 — catch all: startup must never fail due to VS issues
        _log.warning("VectorStore pre-warm failed (will retry on first query): %s", exc)

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

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler: log the real error server-side but return a generic
    message to the client so that internal details are never leaked."""
    _log.error("Unhandled exception on %s %s", request.method, request.url, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试。"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
