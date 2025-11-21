import json
import logging
from typing import Callable, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(
        self,
        topics: list,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "default-group"
    ):
        """Initialize Kafka consumer."""
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(
            f"Kafka consumer initialized for topics {topics}, "
            f"group: {group_id}"
        )

    def consume(self, handler: Callable[[Dict[str, Any]], None]):
        """Consume messages and call handler for each message."""
        try:
            for message in self.consumer:
                try:
                    logger.info(
                        f"Received message from topic {message.topic}, "
                        f"partition {message.partition}, offset {message.offset}"
                    )
                    handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
        finally:
            self.close()

    def close(self):
        """Close the consumer."""
        self.consumer.close()
        logger.info("Kafka consumer closed")

