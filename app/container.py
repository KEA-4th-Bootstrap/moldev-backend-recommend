from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Factory, Singleton

from app.recommend.adapter.output.azureai.category_gpt import GPTAdapter
from app.recommend.adapter.output.pinecone.repository import VectorRepositoryAdapter
from app.recommend.application.service.recommend import RecommendService
from app.recommend.adapter.output.mongo.user_item_repository import UserItmeRepositoryAdapter
from app.recommend.adapter.output.mongo.post_categories_repository import PostCategoriesRepositoryAdapter


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["app"])

    vector_repository_adapter = Singleton(VectorRepositoryAdapter)
    user_item_repository_adapter = Singleton(UserItmeRepositoryAdapter)
    post_categories_repository_adapter = Singleton(PostCategoriesRepositoryAdapter)
    category_gpt_adapter = Singleton(GPTAdapter)
    recommend_service = Singleton(RecommendService,
                                  vector_repo=vector_repository_adapter,
                                  user_item_repo=user_item_repository_adapter,
                                  post_categories_repo=post_categories_repository_adapter,
                                  category_gpt=category_gpt_adapter)
