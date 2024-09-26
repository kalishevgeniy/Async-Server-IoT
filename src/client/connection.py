import asyncio
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connector.abstract import ConnectorAbstract
from src.protocol.abstract import AbstractProtocol
from src.unit.unit import Unit
from src.utils.message import Message


class ClientConnection:

    def __init__(
            self,
            msgs_queue: asyncio.Queue,
            protocol: AbstractProtocol,
            server_status: asyncio.Event,
            connector: ConnectorAbstract,
            authorization: Optional[AbstractAuthorization] = None,
            *args,
            **kwargs
    ):
        self.msgs_queue: asyncio.Queue[Message] = msgs_queue
        self.protocol: AbstractProtocol = protocol
        self.server_status: asyncio.Event = server_status
        self.authorization: AbstractAuthorization = authorization
        self.connector = connector

        self.unit = Unit(
            protocol=self.protocol,
            authorization=self.authorization
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
                    for message in messages:
                        await self.msgs_queue.put(message)

                await self.connector.send(answer)

            else:
                await asyncio.sleep(0.01)

            if self.connector.is_not_alive:
                break

    async def close_connection(self):
        await self.connector.close_connection()
