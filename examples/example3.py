import asyncio
import logging

from fast_api_ex1 import FastApiServer


async def main() -> None:
    fast_api_server = FastApiServer()
    await fast_api_server.serve()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())
