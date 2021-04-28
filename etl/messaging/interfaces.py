"""Describes interface for sending messages to a message broker"""
import abc


class MessageProducer(abc.ABC):
    """Interface for message producer backend"""

    @abc.abstractmethod
    def job_created(self, job_id: str, filename: str, handler: str, uploader: str) -> None:
        """Send a message indicating a new job has been created
        :param job_id: Unique ID for new job
        :param filename: The data file that is being processed
        :param handler: The filename of the processor config
        :param uploader: The username of who initiated the process
        """
        raise NotImplementedError

    @abc.abstractmethod
    def job_evt_task(self, job_id: str, task: str) -> None:
        """Send a message signalling an event about a job has occurred
        :param job_id: The id the job this event is about
        :param task: Indicates which task the job is starting
        """
        raise NotImplementedError

    @abc.abstractmethod
    def job_evt_status(self, job_id: str, status: str) -> None:
        """Send a message signalling an event about a job has occurred
        :param job_id: The id the job this event is about
        :param status: 'success' or 'failure'
        """
        raise NotImplementedError

    @abc.abstractmethod
    def job_evt_progress(self, job_id: str, progress: float) -> None:
        """Send a message signalling an event about a job has occurred
        :param job_id: The id the job this event is about
        :param progress: Indicates overall progress of the job [0.0, 1.0]
        """
        raise NotImplementedError

    @abc.abstractmethod
    def job_evt_committed(self, job_id: str, committed: int) -> None:
        """Send a message signalling an event about a job has occurred
        :param job_id: The id the job this event is about
        :param committed: Claims records inserted by the job
        """
        raise NotImplementedError
