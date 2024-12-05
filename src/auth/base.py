import uuid
from typing import Optional

from src.auth.abstract import AbstractAuthorization, T


class BaseAuthorization(AbstractAuthorization):

    async def authorized_in_system(
            self,
            imei: str,
            password: Optional[str] = None
    ) -> T:
        self.id = uuid.uuid4().hex
        return self.id
