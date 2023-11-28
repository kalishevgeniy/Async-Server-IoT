import os

from src.publisher.rabbitmq.publisher import RabbitPublisher


class Publisher:
    class_publisher = RabbitPublisher

    host: str = 'rabbitmq'
    port: int = 5672
    login: str = os.getenv('RABBITMQ_DEFAULT_USER', 'test')
    password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'test')

    exchange: str = "messages_from_iot"
    routing_key: str = "{manufacture}{model}{imei}"
