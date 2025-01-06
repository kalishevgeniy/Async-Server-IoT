import asyncio


LOGIN = b'#L#2.0;860000000000000;NA;46D4\r\n'
DATA = (
    b'#D#010125;112233;5128.199596;N;00000.122544;E;0;0;0;0;0;0;NA;;NA;'
    b'example1:1:0,example2:2:0.12,example3:1:123;72D3\r\n'
)


async def main():
    reader, writer = await asyncio.open_connection(
        '0.0.0.0',
        50_000
    )

    writer.write(LOGIN)
    await writer.drain()

    answer = await reader.read(64)
    print('Login packet answer', answer)

    try:
        while True:
            writer.write(DATA)
            await writer.drain()

            answer = await reader.read(64)

            if answer == b'server_off\r\n':
                print('Server off')
                break

            print('Data packet answer', answer)

            await asyncio.sleep(5)
    except KeyboardInterrupt as e:
        print('Stop sending data')

    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
