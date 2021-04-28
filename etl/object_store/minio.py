"""Contains the Minio implementation of the object store backend interface"""
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any, Iterable, Optional, Protocol

from minio import Minio

from etl.config import settings
from etl.object_store.interfaces import EventType, ObjectEvent, ObjectStore
from etl.object_store.object_id import ObjectId

KEEP_FILENAME = '.keep'

class MinioObjectResponse(Protocol):
    """A duck type interface describing the minio object response"""
    data: bytes
    def close(self):
        """Closes this response object"""

notification = {'QueueConfigurations': [
    {
        'Id': 'id',
        'Arn': settings.minio_notification_arn,
        'Events': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*']
    }
]}

class MinioObjectStore(ObjectStore):
    """Implements the ObjectStore interface using Minio as the backend service"""
    def __init__(self):
        self._minio_client = Minio(
            settings.minio_host,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

        # Create bucket notification
        if not self._minio_client.bucket_exists(settings.minio_etl_bucket):
            self._minio_client.make_bucket(settings.minio_etl_bucket)
        self._minio_client.set_bucket_notification(settings.minio_etl_bucket, notification)

    def download_object(self, src: ObjectId, dest_file: str) -> None:
        self._minio_client.fget_object(src.namespace, src.path, dest_file)

    def upload_object(self, dest: ObjectId, src_file: str) -> None:
        self._minio_client.fput_object(dest.namespace, dest.path, src_file)

    def read_object(self, obj: ObjectId) -> bytes:
        response: Optional[MinioObjectResponse] = None
        try:
            response = self._minio_client.get_object(obj.namespace, obj.path)
            if response is None:
                raise KeyError()
            return response.data
        finally:
            if response:
                response.close()

    def write_object(self, obj: ObjectId, data: bytes) -> None:
        self._minio_client.put_object(obj.namespace, obj.path, BytesIO(data), len(data))

    def move_object(self, src: ObjectId, dest: ObjectId) -> None:
        self._minio_client.copy_object(dest.namespace, dest.path, f'{src.namespace}/{src.path}')
        self._minio_client.remove_object(src.namespace, src.path)

    def delete_object(self, obj: ObjectId) -> None:
        self._minio_client.remove_object(obj.namespace, obj.path)

    def ensure_directory_exists(self, directory: ObjectId) -> None:
        if not next(self._minio_client.list_objects(directory.namespace, directory.path), None):
            keep_file_path = str(PurePosixPath(directory.path).joinpath(KEEP_FILENAME))
            self.write_object(ObjectId(directory.namespace, keep_file_path), b'')

    def parse_notification(self, evt_data: Any) -> ObjectEvent:
        bucket_name, file_name = evt_data['Key'].split('/', 1)
        object_id = ObjectId(bucket_name, file_name)
        event_type = EventType.Delete if evt_data['EventName'].startswith('s3:ObjectRemoved') else EventType.Put
        return ObjectEvent(object_id, event_type)

    def list_objects(self, namespace: str, path: Optional[str] = None, recursive=False) -> Iterable[ObjectId]:
        for minio_object in self._minio_client.list_objects(namespace, path, recursive):
            yield ObjectId(minio_object.bucket_name, minio_object.object_name)

    def retrieve_object_metadata(self, src: ObjectId) -> dict:
        return self._minio_client.stat_object(src.namespace, src.path).metadata
