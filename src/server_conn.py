import asyncio
from asyncio import StreamReader, StreamWriter
from asyncio import Queue


class ClientConnection:

    __slots__ = (
        "reader", "writer",
        "reader_queue",
        "_task_reader"
    )

    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer

        self.reader_queue = Queue()
        self._task_reader = asyncio.create_task(self._reader_from_socket())

    @property
    def is_not_alive(self) -> bool:
        """
        Check task socket reader
        If task finished -> connection close -> return True
        :return: bool
        """
        if self._task_reader.done():
            return True
        return False

    @property
    def new_data(self) -> bool:
        """
        Check data in reader_queue
        If exist new data -> return True
        :return: bool (flag new data)
        """
        if self.reader_queue.empty():
            return False
        return True

    def execute_data(self) -> bytes:
        """
        Execute data from reader_queue, until he will br empty
        :return: bytes (data from socket)
        """
        data_return = list()
        while not self.reader_queue.empty():
            data_return.append(self.reader_queue.get_nowait())
        return b''.join(data_return)

    def get_socket(self):
        """
        Get client socket object
        :return: socket
        """
        return self.writer.get_extra_info('socket')

    async def _reader_from_socket(self):
        """
        Task for reading from socket
        :return: bool
        """
        while True:
            data = await self.reader.read(1_000)

            if not data:
                return True

            await self.reader_queue.put(data)

    async def close_connection(self):
        """
        Make soft close client connection
        :return: None
        """
        self.writer.close()
        try:
            await asyncio.wait_for(
                self.writer.wait_closed(),
                15
            )
        except TimeoutError:
            self._task_reader.cancel()

    async def send_to_unit(self, data: bytes):
        """
        Send packets to writer queue
        :param data: bytes
        :return: None
        """
        if data:
            self.writer.write(data)
            await self.writer.drain()
