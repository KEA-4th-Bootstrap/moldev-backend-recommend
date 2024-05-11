from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    MONGO_DB_URL: str = ""


config: Config = Config()
