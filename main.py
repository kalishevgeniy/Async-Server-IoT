import asyncio
import functools

from src.protocol import protocols
from src.protocol.abstract import AbstractProtocol

from src.publisher.abstract import AbstractPublisher
from src.publisher.redis.publisher import RedisPublisher
from src.status.server_status.connection import ClientConnectionsKeeper
from src.status.server_status.server import ServerKeeper
from src.unit.unit import UnitCommunication
from src.server_conn import ClientConnection


def pre_run_server_connection(func):
    async def exception_analyze(
            *args,
            client_conn_keeper,
            **kwargs
    ):
        self, reader, writer = args
        client_conn = ClientConnection(reader=reader, writer=writer)
        client_conn_keeper.add(asyncio.current_task())

        try:
            print('pre connect')
            return await func(
                self,
                client_conn=client_conn,
                **kwargs
            )
        except NotImplementedError:
            print(f"Warning! Method not implemented")
        except Exception as e:
            print(f"Unknown exception! {e}")
        finally:
            # make soft disconnect
            await client_conn.close_connection()

            # remove curr task from event loop
            # use for keeping connection
            client_conn_keeper.remove_curr_task(asyncio.current_task())

    return exception_analyze


class Server:

    @pre_run_server_connection
    async def run_server_connection(
            self,
            server_status: ServerKeeper,
            client_conn: ClientConnection,
            protocol_handler: AbstractProtocol,
            publisher: AbstractPublisher,
    ):
        """
        Main loop of client connection
        All correct connect/disconnect make in decorator
        All manipulation need user by obj client_conn

        1) Get packets from socket by protocol
        2) Make packet analyze (loging, data parsing etc)
        3) Check status point 2)
            4) if status incorrect make fail answer and break connection
        4) if status is correct make answer for unit
        5) repeat 1) -> 2) ....
        """
        print('new connect')
        unit = UnitCommunication(protocol_handler=protocol_handler)

        await asyncio.sleep(0)
        while server_status.is_work or client_conn.new_data:

            if client_conn.new_data:

                bytes_data = client_conn.execute_data()
                unit.update_buffer(bytes_data)

                packet = unit.get_packet()

                if not packet:
                    continue

                status, data = unit.analyze_packet(packet)

                if not status.correct:
                    answer_fail = unit.create_answer_failed(status)
                    await client_conn.send_to_unit(answer_fail)
                    break

                answer = unit.create_answer(status)
                await publisher.publish_to_destination(data, unit.get_imei)
                await client_conn.send_to_unit(answer)

            else:
                await asyncio.sleep(0.05)

            if client_conn.is_not_alive:
                break


async def task_server_run(
        port: int,
        protocol_handler: AbstractProtocol,
        server_status: ServerKeeper
):
    """
    Run all protocol in one process
    The server_status is always running until the stop command arrives (SIGINT, SIGTERM)
    """
    print('run task serving')
    client_conn_keeper = ClientConnectionsKeeper()
    redis_publisher = RedisPublisher()

    serv_func = functools.partial(
        Server().run_server_connection,
        protocol_handler=protocol_handler,
        server_status=server_status,
        client_conn_keeper=client_conn_keeper,
        publisher=redis_publisher
    )

    task_server = await asyncio.start_server(
        serv_func,
        host='0.0.0.0',
        port=port,
        reuse_address=True,
        backlog=5_000
    )

    server_status.add_protocol_connection(task_server)
    await task_server.start_serving()

    print('start serving', port)
    while task_server.is_serving():
        await asyncio.sleep(1)

    await client_conn_keeper.try_stop()


async def main():
    server_status = ServerKeeper()

    print('run server')
    async with asyncio.TaskGroup() as tg:
        print('protocols', protocols)
        for protocol in protocols:
            tg.create_task(
                task_server_run(
                    port=protocol.PORT,
                    protocol_handler=protocol(),
                    server_status=server_status
                )
            )

    print("Server stop")

if __name__ == '__main__':
    asyncio.run(main())
