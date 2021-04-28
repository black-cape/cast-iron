"""Describes interface for file notification event handler backends"""
import abc
from typing import Callable, Dict


class TaskSink(abc.ABC):
    """Interface for file notification event handler backend"""

    @abc.abstractmethod
    def start(self, event_callback: Callable[[Dict], None]) -> None:
        """Begins listening for file notification events
        :param event_callback: A callback to invoke for each received event
        """
        raise NotImplementedError
