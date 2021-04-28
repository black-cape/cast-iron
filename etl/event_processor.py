"""Contains the implementation of the EventProcessor class"""
import json
import logging
import os
import subprocess
import tempfile
from typing import Dict

from etl.config import settings
from etl.file_processor_config import (FileProcessorConfig,
                                       load_python_processor, try_loads)
from etl.messaging.interfaces import MessageProducer
from etl.object_store.interfaces import EventType, ObjectStore
from etl.object_store.object_id import ObjectId
from etl.path_helpers import (filename, get_archive_path, get_error_path,
                              get_inbox_path, get_processing_path,
                              glob_matches, parent, rename)
from etl.pizza_tracker import PizzaTracker
from etl.tasking.interfaces import TaskSink
from etl.util import short_uuid

LOGGER = logging.getLogger('cast_iron.etl.worker')


class EventProcessor:

    """A service that processes individual object events"""
    def __init__(self, object_store: ObjectStore, task_runner: TaskSink, message_producer: MessageProducer):
        self._object_store = object_store
        self._task_runner = task_runner
        self._processors: Dict[ObjectId, FileProcessorConfig] = dict()
        self._message_producer = message_producer

        # Load existing config files
        for obj in self._object_store.list_objects(settings.minio_etl_bucket, None, recursive=True):
            if obj.path.endswith('.toml'):
                self._toml_put(obj)

    def process(self, evt_data: Dict) -> None:
        """Object event process entry point"""
        evt = self._object_store.parse_notification(evt_data)

        if evt.event_type == EventType.Delete:
            if evt.object_id.path.endswith('.toml'):
                self._toml_delete(evt.object_id)
            return

        if evt.object_id.path.endswith('.toml'):
            self._toml_put(evt.object_id)
        else:
            self._file_put(evt.object_id)

    def _toml_put(self, toml_object_id: ObjectId) -> bool:
        """Handle put event with TOML extension.
        :return: True if the operation is successful.
        """
        try:
            obj = self._object_store.read_object(toml_object_id)
            data: str = obj.decode('utf-8')
            cfg: FileProcessorConfig = try_loads(data)

            if cfg.enabled:
                # Register processor
                self._processors[toml_object_id] = cfg

                self._object_store.ensure_directory_exists(get_inbox_path(toml_object_id, cfg))
                self._object_store.ensure_directory_exists(get_processing_path(toml_object_id, cfg))
                self._object_store.ensure_directory_exists(get_archive_path(toml_object_id, cfg))
            return True
        except ValueError:
            # Raised if we fail to parse and validate config
            return False

    def _toml_delete(self, toml_object_id: ObjectId) -> bool:
        """Handle remove event with TOML extension.
        :return: True if the object was deleted
        """
        return bool(self._processors.pop(toml_object_id, None))

    def _file_put(self, object_id: ObjectId) -> bool:
        """Handle possible data file puts.
        :return: True if successful.
        """
        # pylint: disable=too-many-locals,too-many-branches, too-many-statements
        for config_object_id, processor in self._processors.items():
            if (parent(object_id) != get_inbox_path(config_object_id, processor) or
                    not glob_matches(object_id, config_object_id, processor)):
                # File isn't in our inbox directory or filename doesn't match our glob pattern
                continue

            # Hypothetical file paths for each directory
            processing_file = get_processing_path(config_object_id, processor, object_id)
            archive_file = get_archive_path(config_object_id, processor, object_id)
            error_file = get_error_path(config_object_id, processor, object_id)
            error_log_file_name = f'{filename(object_id).replace(".", "_")}_error_log.txt'
            error_log_file = get_error_path(config_object_id, processor, rename(object_id, error_log_file_name))

            job_id = short_uuid()
            self._message_producer.job_created(job_id, filename(object_id), filename(config_object_id), 'castiron')

            # mv to processing
            self._object_store.move_object(object_id, processing_file)

            with tempfile.TemporaryDirectory() as work_dir:
                # Download to local temp working directory
                local_data_file = os.path.join(work_dir, filename(object_id))
                self._object_store.download_object(processing_file, local_data_file)
                metadata = self._object_store.retrieve_object_metadata(processing_file)
                with open(os.path.join(work_dir, 'out.txt'), 'w') as out, \
                     PizzaTracker(self._message_producer, work_dir, job_id) as pizza_tracker:

                    if processor.shell is not None:
                        env = {
                            'DATABASE_HOST': settings.database_host,
                            'DATABASE_PASSWORD': settings.database_password,
                            'DATABASE_PORT': str(settings.database_port),
                            'DATABASE_TABLE': str(settings.database_table),
                            'DATABASE_USER': str(settings.database_user),
                            'ETL_FILENAME': local_data_file,
                            'PIZZA_TRACKER': pizza_tracker.pipe_file_name,
                            'ETL_FILE_METADATA': json.dumps(metadata)
                        }

                        proc = subprocess.Popen(processor.shell,
                                                shell=True,
                                                executable='/bin/bash',
                                                env=env,
                                                stderr=subprocess.STDOUT,
                                                stdout=out if processor.save_error_log else subprocess.DEVNULL)

                        while True:
                            exit_code = None
                            try:
                                exit_code = proc.wait(.5)
                            except subprocess.TimeoutExpired:
                                pass

                            pizza_tracker.process()

                            if exit_code is not None:
                                break
                        success = exit_code == 0

                    elif processor.python is not None:
                        try:
                            run_method = load_python_processor(processor.python)
                            method_kwargs = {}
                            if processor.python.supports_pizza_tracker:
                                method_kwargs['pizza_tracker'] = pizza_tracker.pipe_file_name
                            if processor.python.supports_metadata:
                                method_kwargs['file_metadata'] = metadata

                            run_method(local_data_file, **method_kwargs)
                            success = True
                        except Exception as exc:  # pylint: disable=broad-except
                            out.write(
                                'Failed to execute the Python worker using the configs '
                                f'{processor.python.dict()} due to {exc}'
                            )
                            success = False

                    else:
                        LOGGER.error('No shell or python configuration set.')
                        return False

                    if success:
                        # Success. mv to archive
                        self._object_store.move_object(processing_file, archive_file)
                        self._message_producer.job_evt_status(job_id, 'success')
                    else:
                        # Failure. mv to failed
                        self._object_store.move_object(processing_file, error_file)
                        self._message_producer.job_evt_status(job_id, 'failure')

                        # Optionally save error log to failed
                        if processor.save_error_log:
                            self._object_store.upload_object(error_log_file, os.path.join(work_dir, 'out.txt'))

                # Success or not, we handled this
                return True

        # Not our table
        return False
