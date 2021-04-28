"""Contains implementation of MessageProducer backend using Kafka"""
from json import dumps

from kafka import KafkaProducer

from etl.config import settings
from etl.messaging.interfaces import MessageProducer


class KafkaMessageProducer(MessageProducer):
    """Implementation of MessageProducer backend using Kafka"""

    def __init__(self):
        self._producer = KafkaProducer(bootstrap_servers=[settings.kafka_broker],
                                       value_serializer=lambda x: dumps(x).encode('utf-8'))

    def job_created(self, job_id: str, filename: str, handler: str, uploader: str) -> None:
        self._producer.send(settings.kafka_pizza_tracker_topic, {
            'type': 'job_created',
            'job_id': job_id,
            'filename': filename,
            'handler': handler,
            'uploader': uploader
        })

    def job_evt_task(self, job_id: str, task: str) -> None:
        self._producer.send(settings.kafka_pizza_tracker_topic, {
            'type': 'job_update',
            'job_id': job_id,
            'task': task
        })

    def job_evt_status(self, job_id: str, status: str) -> None:
        self._producer.send(settings.kafka_pizza_tracker_topic, {
            'type': 'job_update',
            'job_id': job_id,
            'status': status
        })

    def job_evt_progress(self, job_id: str, progress: float) -> None:
        self._producer.send(settings.kafka_pizza_tracker_topic, {
            'type': 'job_update',
            'job_id': job_id,
            'progress': progress
        })

    def job_evt_committed(self, job_id: str, committed: int) -> None:
        self._producer.send(settings.kafka_pizza_tracker_topic, {
            'type': 'job_update',
            'job_id': job_id,
            'committed': committed
        })
