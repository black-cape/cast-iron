"""Entry point for ETL worker"""
from etl.event_processor import EventProcessor
from etl.messaging.kafka import KafkaMessageProducer
from etl.object_store.minio import MinioObjectStore
from etl.tasking.faust import FaustTaskSink

message_producer = KafkaMessageProducer()
task_sink = FaustTaskSink()
object_store = MinioObjectStore()
event_processor = EventProcessor(object_store, task_sink, message_producer)

task_sink.start(event_processor.process)
