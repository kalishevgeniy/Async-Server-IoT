### ASYNC SERVER IOT

This is an asynchronous TCP server for receiving data from IOT devices (GPS trackers, smart devices, etc.) written in Python. Data reception is performed according to the principle of first login (packet with authorization data), then data packets (packets with cooridnates, sensors). The server supports responses to devices.

The server is written in such a way that each developer can add his own data transfer protocols (using existing interfaces)


## HOW USE

Import the desired protocol from the `src.protocol` folder. Assign the server `host` and `port`, you can also pass any other arguments that the `asyncio` module's `start_server` method accepts, such as `reuse_address` or `ssl_shutdown_timeout`.

```
import asyncio
from src.protocol.gurtam.wialon_ips_v2 import WialonIPSv2
from src.server.server import IoTServer
import logging

logging.basicConfig(
    level=logging.DEBUG
)


async def main() -> None:
    async with IoTServer(
            host="0.0.0.0",
            port=50_000,
            protocol=WialonIPSv2
    ) as server:
        async for message in server:
            print(message)


if __name__ == '__main__':
    asyncio.run(main())

```
## WRITING YOUR PROTOCOL

To write your own protocol, you need to inherit from the `AbstractProtocol` class and implement its interface.

```
from src.protocol.abstract import AbstractProtocol


class MyProtocol(AbstractProtocol):
    pass
```

## FUTURE
- Adding application specific exceptions
- Finalization of documentation
- Adding tests
- Support of additional data transfer protocols (Teltonika, WialonIPS2 supported)
- Support for UDP data transfer
- Further refinement of PEP8 code, bug fixing, refactoring
- Sending commands to devices
