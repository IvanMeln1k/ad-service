import json

from aiokafka import AIOKafkaProducer

from src.events.publisher import EventPublisher


class KafkaEventPublisher(EventPublisher):
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8"),
        )

    async def publish(self, topic: str, key: str, value: dict) -> None:
        await self.producer.send_and_wait(topic, key=key, value=value)

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()
