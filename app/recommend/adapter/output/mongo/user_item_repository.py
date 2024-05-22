from app.recommend.adapter.output.mongo.config import user_item

categories = [
    "백엔드", "프론트엔드", "인공지능", "데브옵스", "인프라", "웹", "서버", "데이터베이스", "리눅스", "앱 네이티브",
    "플러터", "자바스크립트", "어셈블리", "딥러닝", "머신러닝", "데이터과학", "대외활동", "동아리", "공모전", "해커톤",
    "트러블슈팅", "네트워크", "운영체제", "컴퓨터구조", "알고리즘", "자료구조", "코딩테스트"
]


class UserItmeRepositoryAdapter:
    def __init__(self):
        self.user_item = user_item

    def get_all_items(self):
        all_items = self.user_item.find()
        result = []
        for idx, item in enumerate(all_items):
            values = [item["items"].get(category, 0) for category in categories]
            result.append({
                "id": item["user_id"],
                "values": values
            })
        return result

    async def get_user_item(self, user_id: int):
        return self.user_item.find_one({"user_id": user_id})

    async def insert_user_item(self, user_id: int, items: dict):
        self.user_item.insert_one({"user_id": user_id, "items": items})

    async def inc_items(self, user_id: int, item_names: list):
        self.user_item.update_one(
            {"user_id": user_id},
            {"$inc": {f"items.{item_name}": 1 for item_name in item_names}},
            upsert=True)
