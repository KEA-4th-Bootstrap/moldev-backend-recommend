from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.container import Container
from app.recommend.adapter.input import router as recommend_router
from app.recommend.adapter.input.kafka_consumer import KafkaConsumerManager

from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    ResponseLogMiddleware,
)

import logging

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


def init_routers(app_: FastAPI) -> None:
    container = Container()
    recommend_router.container = container
    app_.include_router(recommend_router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def init_consumer(app_: FastAPI) -> None:
    @app_.on_event("startup")
    async def startup_event():
        consumer_manager = KafkaConsumerManager.get_instance()
        await consumer_manager.start_consumer()
        log.info("Kafka consumer started")

    @app_.on_event("shutdown")
    async def shutdown_event():
        consumer_manager = KafkaConsumerManager.get_instance()
        await consumer_manager.stop_consumer()
        log.info("Kafka consumer stopped")


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(ResponseLogMiddleware),
    ]
    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="molDev",
        description="Recommendation API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )

    init_listeners(app_=app_)
    init_routers(app_=app_)
    init_consumer(app_=app_)
    return app_


app = create_app()
