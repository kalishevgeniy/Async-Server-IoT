import asyncio

from src.auth.base import BaseAuthorization
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
            authorization=BaseAuthorization(),
            protocol=WialonIPSv2
    ) as server:


        while range(0, 10, -1):
            async for connection in server.new_connections:
                print(connection)

            async for message in server.messages:
                print(message)

            await asyncio.sleep(2)

        await asyncio.sleep(10)
        await server.send_command(b'www', 100)

        await asyncio.sleep(10)
        # new_units = server.new_connection()
        # stats = server.stats()
        #
        # messages = server.messages()
        # packets = server.packets()
        #
if __name__ == '__main__':
    asyncio.run(main())
