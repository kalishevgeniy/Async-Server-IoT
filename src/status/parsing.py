from .abstract import Status


class StatusParsing(Status):

    __slots__ = "err", "crc"

    def __init__(self):
        self.err = None
        self.crc = None

    @property
    def correct(self) -> bool:
        return all(
            (not self.err, self.crc)
        )
