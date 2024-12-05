from typing import TypeVar, Optional

from src.auth.interface import AuthorizationInterface


T = TypeVar("T")


class Authorization(Exception):
    ...


class UnitNotExist(Authorization):
    """
    Unit doesn't exist in system
    """


class IncorrectPassword(Authorization):
    """
    Incorrect password
    """


class AbstractAuthorization(AuthorizationInterface):

    _id: T
    _imei: str

    @property
    def id(self) -> T:
        return self._id

    @id.setter
    def id(self, value: T):
        self._id = value

    @property
    def imei(self) -> str:
        return self._imei

    @property
    def is_authorized(self) -> bool:
        if self.id:
            return True
        return False

    async def authorized_in_system(
            self,
            imei: str,
            password: Optional[str] = None,
    ) -> T:
        raise UnitNotExist

    def check_password(self, imei: str, password: str) -> bool:
        return True
