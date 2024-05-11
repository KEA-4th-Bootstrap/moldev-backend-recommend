from fastapi import APIRouter

from app.recommend.adapter.input.recommend import recommend_router as recommend_router

router = APIRouter()
router.include_router(recommend_router, prefix="/api/recommend", tags=["Recommend"])


__all__ = ["router"]
