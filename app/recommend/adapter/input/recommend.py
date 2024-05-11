from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Path

from app.container import Container
from app.recommend.adapter.input.response import RecommendResponse
from app.recommend.application.service.recommend import RecommendService

recommend_router = APIRouter()


@recommend_router.get(
    "/{member_id}",
    response_model=RecommendResponse
)
@inject
async def get_recommendation(
        member_id: Annotated[str, Path(title="The ID of the item to get")],
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    return {"recommend_list": await recommend_service.get_recommend(member_id)}


@recommend_router.post(
    ""
)
@inject
async def update_vector(
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    await recommend_service.update_data()
    return ""
