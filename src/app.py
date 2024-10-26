from contextlib import asynccontextmanager

import loguru
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import clear_mappers

from src.core.fastapi.mapper import start_mapper
from src.core.fastapi.routes import add_routes
from src.dependency.container import Container

load_dotenv()


def create_app(create_db: bool = False, test: bool = False) -> FastAPI:
    container = Container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        loguru.logger.info("Starting Python Micro Framework Data FastAPI Sample App..")

        await db.connect()

        if create_db:
            await db.create_database()

        loguru.logger.info("Start_mapper..")
        start_mapper()

        loguru.logger.info("Started Python Micro Framework Data FastAPI Sample App..")

        yield

        loguru.logger.info("Stopping Python Micro Framework Data FastAPI Sample App..")
        clear_mappers()

        await db.disconnect()

        loguru.logger.info("Stopped Python Micro Framework Data FastAPI Sample App..")

    application = FastAPI(
        title="Internal Portal API",
        version="0.0.1",
        description="REST API and backend services",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        servers=[],
        lifespan=lifespan,
    )
    application.container = container
    db = container.db()

    # logger.info("Add Routes..")

    add_routes(
        [

        ],
        application,
    )

    return application


app = create_app()
