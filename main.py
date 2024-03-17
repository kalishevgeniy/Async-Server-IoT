import asyncio
from src.protocol.gurtam.wialon_ips_v2 import WialonIPSv2
from src.server.server import IoTServer




async def main() -> None:
    server = IoTServer(
        host="0.0.0.0",
        port=20144,
        protocol=WialonIPSv2
    )

    await server.run()
    async for message in server:
        print(message)


if __name__ == '__main__':
    asyncio.run(main())
