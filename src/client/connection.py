import asyncio

from src.client.connector.abstract import ConnectorAbstract
from src.unit.unit import Unit
from src.utils.message import PreMessage


class ClientConnection:

    def __init__(
            self,
            msgs_queue: asyncio.Queue,
            server_status: asyncio.Event,
            connector: ConnectorAbstract,
            unit: Unit,
            *args,
            **kwargs
    ):
        self.msgs_queue: asyncio.Queue[list[PreMessage]] = msgs_queue
        self.server_status: asyncio.Event = server_status
        self.unit: Unit = unit
        self.connector = connector

    async def run_client_loop(self):
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

        await asyncio.sleep(0)
        while self.server_status.is_set():

            if self.connector.new_data:

                bytes_data = self.connector.execute_data()
                self.unit.update_buffer(bytes_data)

                packet = self.unit.get_packet()

                if not packet:
                    continue

                status, messages = self.unit.analyze_packet(packet)

                if not status.correct:
                    answer_fail = self.unit.create_answer(status)
                    await self.connector.send(answer_fail)
                    break

                answer = self.unit.create_answer(status)

                if messages:
                    await self.msgs_queue.put(messages)

                await self.connector.send(answer)

            else:
                await asyncio.sleep(0.01)

            if self.connector.is_not_alive:
                break

    async def close_connection(self):
        await self.connector.close_connection()

    async def send_command(self, command, **kwargs):
        ready_command = self.unit.create_command(
            command=command,
            **kwargs
        )
        await self.connector.send(ready_command)
