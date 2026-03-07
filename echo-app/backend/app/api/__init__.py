from app.api.users import router as users_router
from app.api.records import router as records_router
from app.api.diaries import router as diaries_router
from app.api.reviews import router as reviews_router

__all__ = ["users_router", "records_router", "diaries_router", "reviews_router"]
