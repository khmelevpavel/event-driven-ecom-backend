import json
import logging
from typing import Any, Dict
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """Initialize Kafka producer."""
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3
        )
        logger.info(f"Kafka producer initialized with servers: {bootstrap_servers}")

    def publish(self, topic: str, event: Dict[str, Any], key: str = None):
        """Publish an event to a Kafka topic."""
        try:
            future = self.producer.send(topic, value=event, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Event published to topic {topic}, "
                f"partition {record_metadata.partition}, "
                f"offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish event to topic {topic}: {e}")
            return False

    def close(self):
        """Close the producer."""
        self.producer.close()
        logger.info("Kafka producer closed")

