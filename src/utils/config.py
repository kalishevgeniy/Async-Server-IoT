from typing import Annotated, Any

from pydantic import BaseModel, AfterValidator, ConfigDict
from pydantic.networks import IPvAnyAddress


def check_port(v: int) -> int:
    assert 0 < v <= 65535
    return v


Port = Annotated[int, AfterValidator(check_port)]


class ServerConfig(BaseModel):
    host: IPvAnyAddress
    port: Port

    local_buffer_size: int = 1024
    queue_size: int = 10_000

    model_config = ConfigDict(extra='allow')


if __name__ == '__main__':
    config = ServerConfig(
        host='0.0.0.0',
        port=2424,
        awdadw=12,
        dad=4124,
    )

    config2 = ServerConfig(
        host='0.0.0.0',
        port=2424,
    )
    print(config.model_extra)
    print(config2.model_extra)
