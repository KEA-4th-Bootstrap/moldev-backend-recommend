from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    email: str = Field(..., description="Email")
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    nickname: str = Field(..., description="Nickname")
    lat: float = Field(..., description="Lat")
    lng: float = Field(..., description="Lng")
