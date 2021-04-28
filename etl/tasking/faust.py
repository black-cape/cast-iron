"""Contains the Faust implementation of the TaskSink backend interface"""
from typing import AsyncIterable, Callable, Dict, Optional

import faust

from etl.config import settings
from etl.tasking.interfaces import TaskSink


class FaustTaskSink(TaskSink):
    """Implementation of TaskSink using Faust"""
    def __init__(self):
        self._event_callback: Callable[[Dict], None] = None

        self._app = faust.App(
            settings.worker_name,
            broker=f'kafka://{settings.kafka_broker}',
            value_serializer='raw'
        )
        self._minio_topic: faust.TopicT = self._app.topic(settings.kafka_minio_topic, value_serializer='json')
        self._app.agent(self._minio_topic)(self._file_evt)
        self._worker: Optional[faust.Worker] = None

    async def _file_evt(self, evts: AsyncIterable[Dict]) -> None:
        async for evt in evts:
            self._event_callback(evt)

    def start(self, event_callback: Callable[[Dict], None]) -> None:
        self._event_callback = event_callback
        self._worker = faust.Worker(self._app, loglevel='info')
        self._worker.execute_from_commandline()
