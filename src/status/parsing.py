from .abstract import Status
from ..protocol.abstract import AbstractProtocol


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

    def make_answer(
            self,
            metadata: dict,
            handler: AbstractProtocol
    ) -> bytes:
        if self.correct:
            return handler.answer_packet(
                status=self,
                metadata=metadata
            )
        else:
            return handler.answer_failed_data_packet(
                status=self,
                metadata=metadata
            )
