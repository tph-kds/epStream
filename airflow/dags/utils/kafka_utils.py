import time
import logging
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def kafka_ready(broker: str, timeout_s: int = 120, interval_s: int = 5) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            KafkaAdminClient(bootstrap_servers=broker).close()
            return True
        except NoBrokersAvailable:
            time.sleep(interval_s)
    raise RuntimeError(f"Kafka broker {broker} not ready")

def ensure_kafka_topic_exists(broker: str, topics: list[dict]) -> None:
    """
    topics = [{"name": "comments.raw", "partitions": 3, "replication_factor": 1}, ...]
    """
    admin = KafkaAdminClient(bootstrap_servers=broker)
    existing = set(admin.list_topics())
    new_topics = []
    for t in topics:
        name = t["name"]
        if name in existing:
            continue
        new_topics.append(NewTopic(
            name=name,
            num_partitions=int(t.get("partitions", 1)),
            replication_factor=int(t.get("replication_factor", 1))
        ))
    if new_topics:
        try:
            admin.create_topics(new_topics=new_topics, validate_only=False)
            logger.info(f"Created topics: {[t.name for t in new_topics]} successfully")
        except TopicAlreadyExistsError:
            logger.warning(f"Topics already exist: {[t.name for t in new_topics]}")
            pass
    admin.close()