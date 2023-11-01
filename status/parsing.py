from ..status.abstract import Status


class StatusParsing(Status):

    __slots__ = "_err", "_crc"

    def __init__(self):
        self._err = None
        self._crc = None

    @property
    def correct(self) -> bool:
        return all(
            (not self._err, self._crc)
        )

    @property
    def error(self):
        return self._err

    @error.setter
    def error(self, value):
        self._err = value

    @property
    def crc(self):
        return self._crc

    @crc.setter
    def crc(self, value):
        self._crc = value
