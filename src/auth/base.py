import uuid
from typing import Optional

from src.auth.abstract import AbstractAuthorization


class BaseAuthorization(AbstractAuthorization):

    async def authorized_in_system(
            self,
            imei: str,
            protocol: str,
            password: Optional[str] = None
    ):
        return uuid.uuid4().hex
