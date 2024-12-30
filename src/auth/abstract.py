from typing import Optional

from src.auth.interface import AuthorizationInterface


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

    async def authorized_in_system(
            self,
            imei: str,
            protocol: str,
            password: Optional[str] = None,
    ):
        raise UnitNotExist
        # raise IncorrectPassword

