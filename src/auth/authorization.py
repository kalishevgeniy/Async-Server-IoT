from typing import Optional


class Auth:

    __slots__ = '_is_authorized', '_imei','_pass'

    def __init__(self):
        self._is_authorized: bool = False
        self._imei: Optional[str] = None
        self._pass: Optional[str] = None

    def authorized_in_system(
            self,
            imei: Optional[str]
    ) -> bool:
        """
        method to check unit in the system for message with login packet
        for connection with imei in all message need use another method
        :return: bool (True - unit in system, False - unit not in system)
        """
        self._imei = imei
        self._is_authorized = True
        return self._is_authorized

    def check_password(
            self,
            imei: Optional[str],
            password: Optional[str]
    ) -> bool:
        """
        Check password unit, if exist on system
        :return:
        """
        self._pass = password
        return True

    @property
    def imei(self) -> str:
        return self._imei

    @property
    def is_authorized(self) -> bool:
        return self._is_authorized