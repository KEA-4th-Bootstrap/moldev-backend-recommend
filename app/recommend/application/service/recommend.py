from app.recommend.adapter.output.pinecone.repository import VectorRepositoryAdapter


class RecommendService:
    def __init__(self, vector_repo: VectorRepositoryAdapter):
        self.vector_repo = vector_repo

    async def update_data(self):
        await self.vector_repo.upsert_data()

    async def get_recommend(self, member_id: str):
        result = await self.vector_repo.get_k_near(member_id)
        return [result.get("matches")[i].get("id") for i in range(2)]
