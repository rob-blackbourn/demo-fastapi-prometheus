"""Use fast api in a class"""

import asyncio
from asyncio import Event
import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import uvicorn

LOGGER = logging.getLogger("fast-api-ex1")


class Greeting(BaseModel):
    message: str


class FastApiServer:

    def __init__(self):
        self.app = FastAPI(lifespan=self.lifespan)
        self.instrumentator = Instrumentator().instrument(self.app)

        self.app.add_api_route(
            "/greet/{name}",
            self.greet,
            methods=["GET"], response_model=Greeting
        )
        self.app.add_api_route(
            "/stop",
            self.stop,
            methods=["GET"],
        )

        self.server = uvicorn.Server(uvicorn.Config(self.app))

    async def greet(self, name: str) -> Greeting:
        LOGGER.info("Greeting request received for: %s", name)
        return Greeting(message=f"Hello {name}")

    async def stop(self) -> str:
        LOGGER.info("Stopping server")
        # Here you can add any cleanup logic if needed
        self.server.should_exit = True
        return "stopping"

    async def tick(self, stop_event: Event) -> None:
        while not stop_event.is_set():
            LOGGER.info("Tick...")
            await asyncio.sleep(10)

    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        LOGGER.info("Starting lifespan context")

        self.instrumentator.expose(app)

        stop_event = Event()
        task = asyncio.create_task(self.tick(stop_event))

        yield

        LOGGER.info("Stopping lifespan context")
        stop_event.set()
        await task

        LOGGER.info("Lifespan context stopped")

    async def serve(self) -> None:
        LOGGER.info("Starting server")
        await self.server.serve()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fast_api_server = FastApiServer()
    asyncio.run(fast_api_server.serve())
