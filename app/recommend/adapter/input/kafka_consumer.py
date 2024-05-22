from random import randint

import aiokafka
import asyncio
import json
import logging
import os
import numpy as np

from app.recommend.adapter.output.azureai.category_gpt import GPTAdapter
from app.recommend.adapter.output.mongo.post_categories_repository import PostCategoriesRepositoryAdapter
from app.recommend.adapter.output.mongo.user_item_repository import UserItmeRepositoryAdapter
from app.recommend.adapter.output.pinecone.repository import VectorRepositoryAdapter
from config import config

# env variables
KAFKA_TOPIC = "update"
KAFKA_CONSUMER_GROUP_PREFIX = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
KAFKA_BOOTSTRAP_SERVERS = config.KAFKA_BOOTSTRAP_SERVERS

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


def normalize_values(all_user_items):
    # 모든 values를 수집
    all_values = np.array([item['values'] for item in all_user_items])

    # 각 열의 최대값과 최소값 계산
    max_values = np.max(all_values, axis=0)
    min_values = np.min(all_values, axis=0)

    # 정규화 함수
    def normalize(value, min_value, max_value):
        return float((value - min_value + 0.001) / (max_value - min_value - 0.001) if max_value != min_value else value)

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


class KafkaConsumerManager:
    _instance = None

    def __init__(self, *,
                 user_item_repo: UserItmeRepositoryAdapter,
                 post_categories_repo: PostCategoriesRepositoryAdapter,
                 vector_repo: VectorRepositoryAdapter,
                 gpt_adapter: GPTAdapter
                 ):
        self.consumer = None
        self.consume_task = None
        self.user_item_repo = user_item_repo
        self.post_categories_repo = post_categories_repo
        self.vector_repo = vector_repo
        self.gpt_adapter = gpt_adapter

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(user_item_repo=UserItmeRepositoryAdapter(),
                                post_categories_repo=PostCategoriesRepositoryAdapter(),
                                vector_repo=VectorRepositoryAdapter(),
                                gpt_adapter=GPTAdapter())
        return cls._instance

    async def start_consumer(self):
        if self.consumer is None:
            group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
            self.consumer = aiokafka.AIOKafkaConsumer(
                KAFKA_TOPIC,
                loop=asyncio.get_event_loop(),
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=group_id
            )
            await self.consumer.start()
            self.consume_task = asyncio.create_task(self.consume_messages())

    async def stop_consumer(self):
        if self.consume_task:
            self.consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def consume_messages(self):
        try:
            async for message in self.consumer:
                # 여기서 메시지를 처리하는 로직 구현
                log.info(f"Received message: {message.value}")
                # 예시: 상태 업데이트 함수 호출
                await self.update_data(message)
        except asyncio.CancelledError:
            log.info("Consumer task was cancelled")
        except Exception as e:
            log.error(f"Error in consumer task: {e}")
        finally:
            log.info("Consumer task has stopped")

    async def update_data(self, message):
        content = json.loads(message.value).get("content")
        member_id = json.loads(message.value).get("memberId")
        post_id = json.loads(message.value).get("postId")
        log.info(f"member_id: {member_id}, post_id: {post_id}")

        if content is None:
            # 카테고리 조회 후 해당 사용자 아이템 업데이트
            categories = await self.post_categories_repo.get_post_categories(post_id)
            log.info(f"categories: {categories['categories']}")
            await self.user_item_repo.inc_items(member_id, categories['categories'])
        else:
            # 카테고리 추출 후 저장, 사용자 아이템 업데이트
            categories = await self.gpt_adapter.extract_category(content)
            log.info(f"categories: {categories['categories']}")
            await self.post_categories_repo.insert_post_categories(post_id, categories.split(","))
            await self.user_item_repo.inc_items(member_id, categories.split(","))

        # 벡터DB 업데이트
        items = self.user_item_repo.get_all_items()
        log.info(items)
        items = normalize_values(items)
        await self.vector_repo.upsert_data(items)
