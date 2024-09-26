import asyncio
from src.protocol import WialonIPSv2
from src.server.server import run_server
import logging

logging.basicConfig(
    level=logging.DEBUG
)


async def main() -> None:

    async with run_server(
            host="0.0.0.0",
            port=50_000,
            protocol=WialonIPSv2
    ) as server:
        async for message in server:
            print(message)

if __name__ == '__main__':
    asyncio.run(main())
