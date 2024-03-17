from typing import Protocol

from src.protocol.abstract import AbstractProtocol


class Status(Protocol):

    def correct(self) -> bool:
        """Check correct all field"""

    def make_answer(
            self,
            metadata: dict,
            handler: AbstractProtocol
    ) -> bytes:
        """Return specific answer for handler"""
