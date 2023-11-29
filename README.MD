### ASYNC SERVER IOT

This is an asynchronous TCP server for receiving data from IOT devices (GPS trackers, smart devices, etc.) written in Python. Data reception is performed according to the principle of first login (packet with authorization data), then data packets (packets with cooridnates, sensors). The server supports responses to devices.

The server is written in such a way that each developer can add his own data transfer protocols (using existing interfaces), add his own destinations for data, as well as his own authorization in the system.

Coming soon:
- Refining data publishing (Redis, RabbitMQ)
- Adding to Kafka publishers
- Adding application specific exceptions
- Finalization of documentation
- Adding tests
- Support of additional data transfer protocols (Teltonika, WialonIPS2 supported)
- Support for UDP data transfer
- Further refinement of PEP8 code, bug fixing, refactoring
- Sending commands to devices
