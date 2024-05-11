from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Factory, Singleton

from app.recommend.adapter.output.pinecone.repository import VectorRepositoryAdapter
from app.recommend.application.service.recommend import RecommendService


class RecommendContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(modules=["app"])

    vector_repository_adapter = Singleton(VectorRepositoryAdapter)
    recommend_service = Singleton(RecommendService, vector_repo=vector_repository_adapter)
