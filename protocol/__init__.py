from ..protocol.gurtam.wialon_ips_v2 import WialonIPSv2
from ..protocol.teltonika.teltonika import Teltonika

__all__ = [
    'protocols',
    'WialonIPSv2', 'Teltonika'
]


protocols = [
    WialonIPSv2,
    Teltonika
]
