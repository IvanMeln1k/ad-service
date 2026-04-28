import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from src.config import config
from src.clients.profiler_client import HttpProfilerClient
from src.clients.notificator_client import HttpNotificatorClient
from src.handler.registration_handler import RegistrationHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    consumer = AIOKafkaConsumer(
        config.KAFKA_TOPIC_REGISTRATIONS,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id=config.KAFKA_GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )

    profiler_client = HttpProfilerClient(base_url=config.PROFILER_URL)
    notificator_client = HttpNotificatorClient(base_url=config.NOTIFICATOR_URL)
    handler = RegistrationHandler(profiler_client, notificator_client)

    await consumer.start()
    logger.info(
        "Profiler Unloader started, listening on topic '%s'",
        config.KAFKA_TOPIC_REGISTRATIONS,
    )

    try:
        async for message in consumer:
            try:
                await handler.handle(message.value)
            except Exception:
                logger.exception("Error processing message: %s", message.value)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
