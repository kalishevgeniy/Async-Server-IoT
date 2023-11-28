from typing import Optional

from .abstract import Status


class StatusAuth(Status):

    __slots__ = "crc", "authorization", "password", "errror"

    def __init__(self):
        self.crc: Optional[bool] = None
        self.authorization: Optional[bool] = None
        self.password: Optional[bool] = None
        self.error = None

    @property
    def correct(self) -> bool:
        return all(
            (self.crc, self.authorization, self.password, not self.error)
        )
