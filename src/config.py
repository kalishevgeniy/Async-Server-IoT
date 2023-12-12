import os
from aio_pika import ExchangeType
import importlib


class Publisher:
    host: str = '0.0.0.0'
    port: int = 5672
    login: str = os.getenv('RABBITMQ_DEFAULT_USER', 'test')
    password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'test')

    exchange: str = "messages_from_iot"
    exchange_type: ExchangeType = ExchangeType.TOPIC

    queue_name: str = "messages_from_iot"
    # routing_key: str = "{manufacture}{model}{imei}"
    routing_key: str = "#"

    @property
    def class_publisher(self):
        return importlib.import_module(
            'src.publisher.rabbitmq.publisher'
        ).RabbitPublisher()

