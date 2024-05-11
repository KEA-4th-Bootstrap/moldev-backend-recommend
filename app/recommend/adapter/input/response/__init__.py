from pydantic import BaseModel, Field


class RecommendResponse(BaseModel):
    recommend_list: list[str] = Field(..., description="Recommend list")
