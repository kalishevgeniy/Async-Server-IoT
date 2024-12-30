import asyncio
from datetime import datetime

from src.auth.abstract import (
    AbstractAuthorization,
    UnitNotExist,
    IncorrectPassword
)
from src.client.connector.abstract import T
from src.protocol.parser import PacketParser
from src.protocol.abstract import AbstractProtocol
from src.protocol.interface import MessageAnnotated
from src.status.abstract import Status
from src.utils.buffer import Buffer
from src.utils.datamanager import DataManager, Packet, Command, Data
from src.utils.unit import Unit


class ClientConnection:

    def __init__(
            self,
            data_manager: DataManager,
            server_status: asyncio.Event,
            connector: T,   # ConnectorAbstract
            authorization: AbstractAuthorization,
            protocol: AbstractProtocol,
            *args,
            **kwargs
    ):
        self.data_manager: DataManager = data_manager
        self.server_status: asyncio.Event = server_status
        self.authorization: AbstractAuthorization = authorization
        self.connector: T = connector
        self.protocol: AbstractProtocol = protocol
        self.unit = Unit()
        self.parser = PacketParser(protocol)
        self.buffer = Buffer(
            handler=protocol,
            *args,
            **kwargs
        )

    def __repr__(self):
        return (
            f'<ClientConnection '
            f'unit={self.unit.imei} '
            f'protocol={self.protocol} '
            f'raddr={self.connector.address}'
            f'>'
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

            if self.connector.new_data or self.buffer.is_not_empty:

                self.buffer.update(self.connector.execute_bytes())

                result = self.parser.parsing(
                    buffer=self.buffer,
                    protocol=self.protocol,
                    unit=self.unit,
                )

                if not result:
                    continue

                status, messages, packet = result

                if status.correct and not self.unit.is_authorized:
                    status = await self._authorization(
                        status=status,
                        unit=self.unit,
                    )

                answer = status.make_answer(
                    handler=self.protocol,
                    unit=self.unit,
                )

                if not status.correct:
                    await self.connector.send(answer)
                    break

                ip, port = self.connector.address
                await self._publish(
                    messages=messages,
                    packet=Packet(
                        packet=packet,
                        client_port=port,
                        client_ip=ip,
                        time_received=datetime.now(),
                    ),
                    answer=answer,
                )

                await self.connector.send(answer)

            else:
                await asyncio.sleep(0.05)

            if self.connector.is_not_alive:
                break

    async def close_connection(self):
        await self.connector.close_connection()

    async def send_command(self, command, **kwargs) -> Command:
        ready_command = self.protocol.create_command(
            unit=self.unit,
            command=command,
        )

        await self.connector.send(ready_command)
        return Command(
            command_send=ready_command,
            command_body=command,
        )

    async def _publish(
            self,
            messages: MessageAnnotated,
            packet: Packet,
            answer: bytes
    ):
        if messages:
            await self.data_manager.messages.put(
                Data(
                    unit=self.unit,
                    message=messages,
                    answer=answer,
                    packet=packet,
                )
            )

    async def _authorization(
            self,
            status: Status,
            unit: Unit
    ) -> Status:
        try:
            unit_id = await self.authorization.authorized_in_system(
                imei=unit.imei,
                protocol=self.protocol.TYPE,
                password=unit.password,
            )
            unit.id = unit_id
        except UnitNotExist as e:
            status.authorization = False
            status.error = str(e)
        except IncorrectPassword as e:
            status.authorization = False
            status.password = False
            status.error = str(e)
        else:
            status.authorization = True
            status.password = True

            await self.data_manager.new_connections.put(unit)

        return status
