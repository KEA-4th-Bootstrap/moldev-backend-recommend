from app.recommend.adapter.output.mongo.config import post_categories


class PostCategoriesRepositoryAdapter:
    def __init__(self):
        self.post_categories = post_categories

    async def get_post_categories(self, post_id: int):
        return self.post_categories.find_one({"post_id": post_id})

    async def insert_post_categories(self, post_id: int, categories: list[str]):
        self.post_categories.insert_one({"post_id": post_id, "categories": categories})
