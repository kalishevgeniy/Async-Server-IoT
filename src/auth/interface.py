from abc import ABCMeta, abstractmethod
from typing import Optional


class AuthorizationInterface(object, metaclass=ABCMeta):

    @abstractmethod
    async def authorized_in_system(
            self,
            imei: str,
            protocol: str,
            password: Optional[str],
    ) -> int:
        """
        method to check unit in the system for message with login packet
        for connection with imei in all message need use another method
        :param imei: imei IoT device
        :param protocol: protocol string name
        :param password: <PASSWORD>
        :return: int (id unit in system)
        """
