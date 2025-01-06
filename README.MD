### Async server IOT
This is an asynchronous TCP server for receiving data from IOT devices (GPS trackers, smart devices, etc.) written in Python. Data reception is performed according to the principle of first login (packet with authorization data), then data packets (packets with cooridnates, sensors). The server supports responses to devices.

The server is written in such a way that each developer can add his own data transfer protocols (using existing interfaces)


## How to use

Import the desired protocol from the `src.protocol` folder. Assign the server `host` and `port`, you can also pass any other arguments that the `asyncio` module's `start_server` method accepts, such as `reuse_address` or `ssl_shutdown_timeout`.

```python3
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
```
## Writing your protocol

To write your own protocol, you need to inherit from the `AbstractProtocol` class and implement its interface.

```python3
from src.protocol.abstract import AbstractProtocol


class MyProtocol(AbstractProtocol):
    pass
```

## Future
- Support more protocols (Teltonika, WialonIPS2 supported)
- Add more tests
- Update docs
- Refactoring PEP8