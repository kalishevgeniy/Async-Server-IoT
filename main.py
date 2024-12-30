import asyncio
import logging

from src.auth.base import BaseAuthorization
from src.protocol import WialonIPSv2
from src.server.server import run_server


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    async with run_server(
            host="0.0.0.0",
            port=50_000,
            authorization=BaseAuthorization(),
            protocol=WialonIPSv2
    ) as server:

        i = 0
        async for message in server.messages.inf():
            print(i, message)

            i += 1

if __name__ == '__main__':
    asyncio.run(main())
