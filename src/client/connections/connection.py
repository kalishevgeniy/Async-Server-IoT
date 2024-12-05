import asyncio
import logging
from time import time
from typing import TypeVar, Optional

from pydantic import BaseModel

from src.auth.abstract import (
    AbstractAuthorization,
    UnitNotExist,
    IncorrectPassword
)
from src.client.connector.abstract import ConnectorAbstract
from src.protocol.abstract import AbstractProtocol
from src.protocol.interface import MessageAnnotated
from src.status import exception_wrapper, StatusParsing, StatusAuth
from src.status.abstract import Status
from src.utils.buffer import Buffer
from src.utils.datamanager import DataManager
from src.utils.meta import MetaData

T = TypeVar('T', bound=ConnectorAbstract)


class Packet(BaseModel):
    time_received: float = time()
    packet: bytes
    client_port: int
    client_ip: str


class Command(BaseModel):
    time_sent: float = time()
    command_body: bytes
    command_send: bytes


class Data(BaseModel):
    packet: Packet
    answer: bytes
    message: list[MessageAnnotated]


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
        self.metadata: MetaData = MetaData()
        self.buffer = Buffer(
            handler=protocol,
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

        await asyncio.sleep(0)
        while self.server_status.is_set():

            if self.connector.new_data:

                bytes_ = self.connector.execute_bytes()
                self.buffer.update(bytes_)

                packet = self._get_packet()

                if not packet:
                    continue

                status, messages = await self._analyze_packet(packet)

                answer = status.make_answer(
                    handler=self.protocol,
                    meta=self.metadata
                )

                if not status.correct:
                    await self.connector.send(answer)
                    break

                await self._publish(
                    messages=messages,
                    packet=packet,
                    answer=answer,
                )

                await self.connector.send(answer)

            else:
                await asyncio.sleep(0.01)

            if self.connector.is_not_alive:
                break

    async def close_connection(self):
        await self.connector.close_connection()

    async def send_command(self, command, **kwargs) -> Command:
        ready_command = self.protocol.create_command(
            imei=self.authorization.imei,
            meta=self.metadata,
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
                    message=[messages]
                    if isinstance(messages, DataManager)
                    else messages,
                    answer=answer,
                    packet=packet,
                )
            )

    def _get_packet(self) -> Optional[Packet]:
        packet = self._get_full(
            is_authorized=self.authorization.is_authorized
        )

        if not packet:
            return None

        ip, port = self.connector.address

        return Packet(
            packet=packet,
            client_port=port,
            client_ip=ip,
        )

    def _get_full(self, is_authorized=True) -> Optional[bytes]:
        message = self.buffer.get_all()

        if is_authorized:
            start = self.protocol.START_BIT_PACKET
            end = self.protocol.END_BIT_PACKET
            length = self.protocol.LEN_PACKET
        else:
            start = self.protocol.START_BIT_LOGIN
            end = self.protocol.END_BIT_LOGIN
            length = self.protocol.LEN_LOGIN

        if start:
            if message.startswith(start):
                start_ind = 0
            elif find := message.find(start) >= 0:
                start_ind = find
            else:
                self.buffer.clear()
                return None

        if end:
            if message.endswith(end):
                end_ind = len(message)
            elif find := message.find(end) > 0:
                end_ind = find
            else:
                return None

        # if start and end and length:
        #     message_ = None
        #     if length == len(message):
        #         message_ = message
        #
        #     self.buffer.clear(length)
        #     return message_
        # elif start and end:
        #     return message[start_ind:end_ind]
        # else:
            ...
            # if is_authorized:
            #         start, end = self.protocol.custom_start_end_packet(
            #             bytes_=message,
            #         )
            #     else:
            #         start, end = self.protocol.custom_start_end_login(
            #             bytes_=message
            #         )
        return None

    async def _analyze_packet(
            self,
            packet: Packet
    ) -> tuple[Status, MessageAnnotated]:
        """
        Entry point for analyze packet
        :param packet: bytes
        :return: tuple[Status, Optional[list[dict]]
        """
        if self.authorization.is_authorized:
            return await self._analyze_data_packet(packet)
        else:
            return await self._analyze_login_packet(packet)

    @exception_wrapper
    async def _analyze_login_packet(
            self,
            login_packet: Packet
    ) -> tuple[StatusAuth, MessageAnnotated]:
        """
        Make parsing login packet
        Check unit is register in system
        :param login_packet: bytes
        :return: tuple[StatusAuth, None]
        """

        status = StatusAuth()

        status.crc = self.protocol.check_crc_login(
            login_packet.packet,
            meta=self.metadata,
        )
        packets = self.protocol.parsing_login_packet(
            login_packet.packet,
            meta=self.metadata,
        )

        try:
            await self.authorization.authorized_in_system(
                imei=packets.imei,
                password=packets.password,
            )
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

            await self.data_manager.messages.put(
                f'New unit {self.authorization.imei} {self.authorization.id}'
            )

        logging.debug(f"Unit: {self.authorization.imei} {status}")

        return status, packets.messages

    @exception_wrapper
    async def _analyze_data_packet(
            self,
            data_packet: Packet
    ) -> tuple[StatusParsing, MessageAnnotated]:
        """
        Analyze data_packet
        Packet parsed by protocol_handler
        :param data_packet:  bytes
        :return:  tuple[StatusParsing, MessageAnnotated]
        """

        status = StatusParsing()
        status.crc = self.protocol.check_crc_data(
            data_packet.packet,
            meta=self.metadata
        )
        packets = self.protocol.parsing_packet(
            data_packet.packet,
            meta=self.metadata
        )

        return status, packets
