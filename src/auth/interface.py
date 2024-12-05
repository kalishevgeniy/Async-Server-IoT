from abc import ABCMeta, abstractmethod
from typing import Optional


class AuthorizationInterface(object, metaclass=ABCMeta):

    @property
    @abstractmethod
    def is_authorized(
            self
    ) -> bool:
        """
        Show current status of authorization.
        :return: bool
        """

    @abstractmethod
    async def authorized_in_system(
            self,
            imei: str,
            password: Optional[str],
    ) -> int:
        """
        method to check unit in the system for message with login packet
        for connection with imei in all message need use another method
        :param imei: imei IoT device
        :param password: <PASSWORD>
        :return: int (id unit in system)
        """

    @abstractmethod
    def check_password(
            self,
            imei: str,
            password: str
    ) -> bool:
        """
        Check password unit, if exist on system
        :param imei: imei IoT device
        :param password: check passwort in client storage
        :return: bool (True - if password is valid, False)
        """
