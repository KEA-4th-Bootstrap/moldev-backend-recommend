from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Path, Request

from app.container import Container
from app.recommend.adapter.input.request import UserItemModifyRequest
from app.recommend.application.service.recommend import RecommendService

import logging

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

recommend_router = APIRouter()


@recommend_router.get(
    "/{member_id}"
)
@inject
async def get_recommendation(
        request: Request,
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    member_id = int(request.headers.get("Authorization"))
    return await recommend_service.get_recommend(member_id)


@recommend_router.get(
    "/all/item"
)
@inject
async def get_all_items(
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    return await recommend_service.get_all_items()


@recommend_router.post(
    ""
)
@inject
async def update_vector(
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    await recommend_service.update_data()
    return ""


@recommend_router.patch(
    ""
)
@inject
async def update_user_item(
        request: UserItemModifyRequest,
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    await recommend_service.update_user_item(request.id, request.categories)
    return ""


@recommend_router.get(
    "/post/content",
)
@inject
async def get_post_categories(
        post_content: Annotated[str, Query(title="The content of post to get categories")],
        recommend_service: RecommendService = Depends(Provide[Container.recommend_service])
):
    log.info(f"post_content: {post_content}")
    return await recommend_service.extract_categories(post_content)
