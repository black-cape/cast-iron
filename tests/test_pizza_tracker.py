# pylint: skip-file
from typing import Optional

from etl.messaging.interfaces import MessageProducer
from etl.pizza_tracker import PizzaTracker


class MockMessageProducer(MessageProducer):
    def job_created(self, job_id: str, filename: str, handler: str, uploader: str) -> None:
        raise NotImplementedError

    def job_evt_task(self, job_id: str, task: str) -> None:
        self.job_id = job_id
        self.task = task

    def job_evt_status(self, job_id: str, status: str) -> None:
        self.job_id = job_id
        self.status = status

    def job_evt_progress(self, job_id: str, progress: float) -> None:
        self.job_id = job_id
        self.progress = progress

    def job_evt_committed(self, job_id: str, committed: int) -> None:
        self.job_id = job_id
        self.committed = committed


def test_handle_task():
    message_producer = MockMessageProducer()
    pt = PizzaTracker(message_producer, 'working_dir', 'job_id')
    expected = 'this task'
    pt._handle_task(expected)
    assert expected == message_producer.task
    assert 'job_id' == message_producer.job_id


def test_handle_committed():
    message_producer = MockMessageProducer()
    pt = PizzaTracker(message_producer, 'working_dir', 'job_id')
    expected = 2713
    pt._handle_committed(str(expected))
    assert expected == message_producer.committed
    assert 'job_id' == message_producer.job_id

def test_handle_progress():
    message_producer = MockMessageProducer()
    pt = PizzaTracker(message_producer, 'working_dir', 'job_id')
    expected = .4
    pt._handle_progress('2 / 5')
    assert expected == message_producer.progress
    assert 'job_id' == message_producer.job_id

    expected = .6
    pt._handle_progress(str(expected))
    assert expected == message_producer.progress
    assert 'job_id' == message_producer.job_id
