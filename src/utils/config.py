from typing import Union

from pydantic.networks import IPvAnyAddress, IPv4Address, IPv6Address

addr = Union[IPv4Address, IPv6Address]


class ServerConfig:
    def __init__(
            self,
            host: Union[str, IPv4Address, IPv6Address],
            port: int,
            local_buffer_size: int = 1024 * 1024,
            timeout: int = 1200,
            queue_size: int = 10_000,
            **kwargs
    ):
        self.host = host                                # type: ignore
        self.port = port
        self.local_buffer_size = local_buffer_size
        self.timeout = timeout
        self.queue_size = queue_size

        self.__attrs = dict()
        for key, val in kwargs.items():
            self.__attrs[key] = val

    def __repr__(self):
        return (
            f"ServerConfig("
            f"ip={self.host},"
            f"port={self.port},"
            f"local_buffer_size={self.local_buffer_size},"
            f"queue_size={self.queue_size},"
            f"kwargs={self.__attrs})"
        )

    @property
    def extra(self) -> dict:
        return self.__attrs

    def __getattr__(self, item):
        return self.__attrs[item]

    @property
    def host(self) -> Union[IPv4Address, IPv6Address]:
        return self._host

    @host.setter
    def host(self, value: Union[str, IPv4Address, IPv6Address]):
        if isinstance(value, (IPv4Address, IPv6Address)):
            self._host = value
        self._host = IPvAnyAddress(value)                   # type:ignore

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        assert 0 < value <= 65535
        self._port = value
