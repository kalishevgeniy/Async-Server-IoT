import asyncio
from typing import Optional

from src.auth.authorization import AbstractAuthorization
from src.client.mixin import ReadeWriterMixin
from src.protocol.abstract import AbstractProtocol
from src.unit.unit import Unit


class ClientConnection(ReadeWriterMixin):

    def __init__(
            self,
            msgs_queue: asyncio.Queue,
            protocol: AbstractProtocol,
            server_status: asyncio.Event,
            authorization: Optional[AbstractAuthorization] = None,
            *args,
            **kwargs
    ):
        self.msgs_queue: asyncio.Queue = msgs_queue
        self.protocol: AbstractProtocol = protocol
        self.server_status: asyncio.Event = server_status
        self.authorization: AbstractAuthorization = authorization

        super().__init__(*args, **kwargs)

    def __hash__(self):
        return asyncio.current_task()

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
            protocol_handler=self.protocol,
            authorization=self.authorization,
        )

        await asyncio.sleep(0)
        while self.server_status.is_set():

            if self.new_data:

                bytes_data = self.execute_data()
                unit.update_buffer(bytes_data)

                packet = unit.get_packet()

                if not packet:
                    continue

                status, data = unit.analyze_packet(packet)

                if not status.correct:
                    answer_fail = unit.create_answer(status)
                    await self.send_to_unit(answer_fail)
                    break

                answer = unit.create_answer(status)
                await self.msgs_queue.put(data)
                await self.send_to_unit(answer)

            else:
                await asyncio.sleep(0.005)

            if self.is_not_alive:
                break
