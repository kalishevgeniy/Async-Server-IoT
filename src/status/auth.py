from typing import Optional

from .abstract import Status


class StatusAuth(Status):

    __slots__ = "_crc", "_auth", "_pass", "_err"

    def __init__(self):
        self._crc: Optional[bool] = None
        self._auth: Optional[bool] = None
        self._pass: Optional[bool] = None
        self._err = None

    @property
    def correct(self) -> bool:
        return all(
            (self._crc, self._auth, self._pass, not self._err)
        )

    @property
    def crc(self):
        return self._crc

    @crc.setter
    def crc(self, value):
        self._crc = value

    @property
    def authorization(self):
        return self._auth

    @authorization.setter
    def authorization(self, value: bool):
        self._auth = value

    @property
    def password(self):
        return self._pass

    @password.setter
    def password(self, value):
        self._pass = value

    @property
    def error(self):
        return self._err

    @error.setter
    def error(self, value):
        self._err = value
