import asyncio
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.reader_writer import ReadeWriter
from src.protocol.abstract import AbstractProtocol
from src.unit.unit import Unit
from src.utils.message import Message


class ClientConnection:

    def __init__(
            self,
            msgs_queue: asyncio.Queue,
            protocol: AbstractProtocol,
            server_status: asyncio.Event,
            authorization: Optional[AbstractAuthorization] = None,
            *args,
            **kwargs
    ):
        self.msgs_queue: asyncio.Queue[Message] = msgs_queue
        self.protocol: AbstractProtocol = protocol
        self.server_status: asyncio.Event = server_status
        self.authorization: AbstractAuthorization = authorization

        self._connector = ReadeWriter(
            *args,
            **kwargs
        )

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
        unit = Unit(
            protocol=self.protocol,
            authorization=self.authorization
        )

        await asyncio.sleep(0)
        while self.server_status.is_set():

            if self._connector.new_data:

                bytes_data = self._connector.execute_data()
                unit.update_buffer(bytes_data)

                packet = unit.get_packet()

                if not packet:
                    continue

                status, messages = unit.analyze_packet(packet)

                if not status.correct:
                    answer_fail = unit.create_answer(status)
                    await self._connector.send_to_unit(answer_fail)
                    break

                answer = unit.create_answer(status)

                if messages:
                    for message in messages:
                        await self.msgs_queue.put(message)

                await self._connector.send_to_unit(answer)

            else:
                await asyncio.sleep(0.01)

            if self._connector.is_not_alive:
                break

    async def close_connection(self):
        await self._connector.close_connection()
