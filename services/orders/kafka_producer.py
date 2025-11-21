import os
import sys
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from shared.kafka_client.producer import KafkaProducer

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

