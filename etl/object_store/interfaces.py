"""Describes interface for object store service backends"""
import abc
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Optional

from etl.object_store.object_id import ObjectId


class EventType(Enum):
    """Enum indicating type of file event"""
    Put = 1
    Delete = 2

@dataclass
class ObjectEvent:
    """Represents an implementation-neutral file event"""
    object_id: ObjectId
    event_type: EventType

class ObjectStore(abc.ABC):
    """Interface for object store service backend"""

    @abc.abstractmethod
    def download_object(self, src: ObjectId, dest_file: str) -> None:
        """Downloads an object to the file system
        :param src: source object
        :param dest_file: local path to save to
        """
        raise NotImplementedError

    @abc.abstractmethod
    def upload_object(self, dest: ObjectId, src_file: str) -> None:
        """Uploads a file to the object store
        :param dest: destination object
        :param src_file: local path to upload
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read_object(self, obj: ObjectId) -> bytes:
        """Reads an object into memory
        :param obj: an object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def write_object(self, obj: ObjectId, data: bytes) -> None:
        """Writes an object from memory
        :param obj: destination
        :param data: object contents
        """
        raise NotImplementedError

    @abc.abstractmethod
    def move_object(self, src: ObjectId, dest: ObjectId) -> None:
        """Moves an object to a new path or namespace
        :param src: source location
        :param dest: destination location
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_object(self, obj: ObjectId) -> None:
        """Deletes an object from object store
        :param obj: the object to delete
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_notification(self, evt_data: Dict) -> ObjectEvent:
        """Converts an event deserialized as a dict to an ObjectEvent
        :param evt_data: The file event as a dict
        """
        raise NotImplementedError

    @abc.abstractmethod
    def ensure_directory_exists(self, directory: ObjectId) -> None:
        """Creates the directory object if it does not exist
        :param directory: The directory to create, if necessary
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_objects(self, namespace: str, path: Optional[str] = None, recursive=False) -> Iterable[ObjectId]:
        """Enumerates all objects under a directory, optionally recursively
        :param namespace: The namespace to search under
        :param path: An optional directory in the namespace to start with
        :param recursive: True to recurse directories, defaults to False
        """
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_object_metadata(self, src: ObjectId) -> dict:
        """Retrieve the metadata for an object.
        :param src: source object
        """
        raise NotImplementedError
