import asyncio
from asyncio import Event
import logging
import random
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
import uvicorn

from .custom_metrics import JobMetric, WorkMetric
from .monitoring import monitor
from .constants import APP_NAME, VERSION, HOST, FQDN

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
            "/do-work/{work_name}",
            self.do_work,
            methods=["GET"],
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

    async def do_job(self, job: int, jobs: int) -> None:
        LOGGER.info("Working on job %d of %d", job + 1, jobs)
        with monitor(JobMetric(HOST, APP_NAME, "something")):
            await asyncio.sleep(random.uniform(0.5, 2.0))

    async def do_work(self, work_name: str) -> str:
        with monitor(WorkMetric(HOST, APP_NAME, work_name)):
            jobs = random.randint(1, 5)
            LOGGER.info("Starting work with %d jobs", jobs)
            for job in range(jobs):
                await self.do_job(job, jobs)

        return "done"

    async def stop(self) -> str:
        LOGGER.info("Stopping server")
        # Here you can add any cleanup logic if needed
        self.server.should_exit = True
        return "stopping"

    async def start(self, stop_event: Event) -> None:
        while not stop_event.is_set():
            LOGGER.info("Tick...")
            await asyncio.sleep(10)

    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        LOGGER.info("Starting lifespan context")

        self.instrumentator.expose(app)

        stop_event = Event()
        task = asyncio.create_task(self.start(stop_event))

        yield

        LOGGER.info("Stopping lifespan context")
        stop_event.set()
        await task

        LOGGER.info("Lifespan context stopped")

    async def serve(self) -> None:
        LOGGER.info("Starting server")
        await self.server.serve()
