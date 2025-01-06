import asyncio
import logging
import signal
from typing import Optional

from src.auth.abstract import AbstractAuthorization, UnitNotExist
from src.protocol import WialonIPSv2
from src.server.server import run_server

logging.basicConfig(level=logging.DEBUG)
IS_WORK = asyncio.Event()
IS_WORK.set()


def handler_stop_service(signum, frame):
    logging.warning(f"Stop service {signum} {frame}")
    IS_WORK.clear()


signal.signal(signal.SIGINT, handler_stop_service)
signal.signal(signal.SIGTERM, handler_stop_service)


class BaseAuthorization(AbstractAuthorization):

    async def authorized_in_system(
            self,
            imei: str,
            protocol: str,
            password: Optional[str] = None
    ):
        if imei == '860000000000000' and protocol == 'wialon_ips_v2':
            return 123456

        raise UnitNotExist


async def main() -> None:

    async with run_server(
            host="0.0.0.0",
            port=50_000,
            authorization=BaseAuthorization(),
            protocol=WialonIPSv2
    ) as server:

        while IS_WORK.is_set():
            async for new_conn in server.new_connections:
                logging.info(f'Connected unit: {new_conn}')

            async for message in server.messages:
                logging.info(f'Message: {message}')

            await asyncio.sleep(1)

        await server.send_command(
            b'server_off',
            123456
        )

if __name__ == '__main__':
    asyncio.run(main())
