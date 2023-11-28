import signal
from asyncio import Event

from src.utils.logger import Logger
from src.utils.singleton import Singleton

"""
Is used to monitor the state of the server_status.
The singleton pattern is used to make it possible to call the class
anywhere in the application
"""


class ServerKeeper(metaclass=Singleton):
    def __init__(self):
        signal.signal(signal.SIGINT, self._signal_event)
        signal.signal(signal.SIGTERM, self._signal_event)

        self._is_work = Event()
        self._is_work.set()

        self._server_sockets = list()

    def add_protocol_connection(self, conn):
        """
        Add all server_status run connection
        :param conn:
        :return:
        """
        self._server_sockets.append(conn)

    def _close_server_connection(self):
        """
        Make close connection if server_status stop self work
        :return:
        """
        for conn in self._server_sockets:
            conn.close()

    def _signal_event(self, _signal, frame):
        """
        Signal from OS
        :param _signal:
        :param frame:
        :return:
        """
        Logger().info(f"Send signal {_signal}. Try stop server_status")
        self._close_server_connection()
        self._is_work.clear()

    @property
    def is_work(self) -> bool:
        return self._is_work.is_set()
