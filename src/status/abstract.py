from typing import Protocol


class Status(Protocol):

    def correct(self) -> bool:
        """Check correct all field"""
