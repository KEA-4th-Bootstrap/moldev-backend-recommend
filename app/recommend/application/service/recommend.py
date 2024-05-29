from app.recommend.adapter.output.azureai.category_gpt import GPTAdapter
from app.recommend.adapter.output.mongo.post_categories_repository import PostCategoriesRepositoryAdapter
from app.recommend.adapter.output.mongo.user_item_repository import UserItmeRepositoryAdapter
from app.recommend.adapter.output.pinecone.repository import VectorRepositoryAdapter

import numpy as np
import httpx

import logging

categories = [
    "백엔드", "프론트엔드", "인공지능", "데브옵스", "인프라", "웹", "서버", "데이터베이스", "리눅스", "앱 네이티브",
    "플러터", "자바스크립트", "어셈블리", "딥러닝", "머신러닝", "데이터과학", "대외활동", "동아리", "공모전", "해커톤",
    "트러블슈팅", "네트워크", "운영체제", "컴퓨터구조", "알고리즘", "자료구조", "코딩테스트"
]

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


def normalize_values(all_user_items):
    # 모든 values를 수집
    all_values = np.array([item['values'] for item in all_user_items])

    # 각 열의 최대값과 최소값 계산
    max_values = np.max(all_values, axis=0) - 0.0001
    min_values = np.min(all_values, axis=0) + 0.0001

    # 정규화 함수
    def normalize(value, min_value, max_value):
        return float((value - min_value) / (max_value - min_value) if max_value != min_value else value)

    # 모든 values 정규화
    normalized_items = []
    for item in all_user_items:
        normalized_values = [
            normalize(value, min_value, max_value)
            for value, min_value, max_value in zip(item['values'], min_values, max_values)
        ]
        normalized_items.append({
            "id": str(item["id"]),
            "values": normalized_values
        })

    return normalized_items


class RecommendService:
    def __init__(self, *,
                 vector_repo: VectorRepositoryAdapter,
                 user_item_repo: UserItmeRepositoryAdapter,
                 post_categories_repo: PostCategoriesRepositoryAdapter,
                 category_gpt: GPTAdapter):
        self.vector_repo = vector_repo
        self.user_item_repo = user_item_repo
        self.post_categories_repo = post_categories_repo
        self.category_gpt = category_gpt

    async def update_data(self):
        items = await self.get_all_items()
        await self.vector_repo.upsert_data(items)

    async def get_recommend(self, member_id: int):
        result = await self.vector_repo.get_k_near(member_id)
        ids = [result.get("matches")[i].get("id") for i in range(1, 6)]
        url = "http://member-service.backend.svc.cluster.local:80/api/member/recommend"
        params = {
            "memberIds": ids
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # 오류가 있는 경우 예외 발생
            return response.json()

    async def update_user_item(self, user_id: int, item_names: list):
        await self.validate_user(user_id)
        await self.user_item_repo.inc_items(user_id, item_names)

    async def get_all_items(self):
        items = self.user_item_repo.get_all_items()
        log.info(items)
        items = normalize_values(items)
        return items

    async def get_post_categories(self, post_id: int):
        return self.post_categories_repo.get_post_categories(post_id)

    async def extract_categories(self, post_content: str):
        return await self.category_gpt.extract_category(post_content)

    async def insert_post_categories(self, post_id: int, categories: list):
        await self.post_categories_repo.insert_post_categories(post_id, categories)

    async def validate_user(self, user_id: int):
        user_item = await self.user_item_repo.get_user_item(user_id)
        if not user_item:
            await self.user_item_repo.insert_user_item(user_id, {category: 0 for category in categories})
