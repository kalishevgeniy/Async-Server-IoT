import signal
from asyncio import Event


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


"""
Is used to monitor the state of the server.
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
        Add all server run connection
        :param conn:
        :return:
        """
        self._server_sockets.append(conn)

    def _close_server_connection(self):
        """
        Make close connection if server stop self work
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
        print(f"Send signal {_signal}. Try stop server")
        self._close_server_connection()
        self._is_work.clear()

    @property
    def is_work(self) -> bool:
        return self._is_work.is_set()
