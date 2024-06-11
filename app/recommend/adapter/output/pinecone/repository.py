from app.recommend.adapter.output.pinecone.config import index


class VectorRepositoryAdapter:

    def __init__(self):
        pass

    async def upsert_data(self, vectors: list):
        index.upsert(
            vectors=vectors,
            namespace="categories"
        )

    async def get_k_near(self, member_id: int):
        return index.query(
            namespace="categories",
            id=str(member_id),
            top_k=6
        )

    async def delete_all(self):
        index.delete(namespace="categories", delete_all=True)
