from app.routers.auth import router as auth_router
from app.routers.farmland import router as farmland_router
from app.routers.upload import router as upload_router
from app.routers.users import router as users_router

__all__ = ["auth_router", "farmland_router", "upload_router", "users_router"]
