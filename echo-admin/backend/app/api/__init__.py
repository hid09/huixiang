from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.dashboard import router as dashboard_router
from app.api.admin_users import router as admin_users_router
from app.api.diaries import router as diaries_router

__all__ = ["auth_router", "users_router", "dashboard_router", "admin_users_router", "diaries_router"]
