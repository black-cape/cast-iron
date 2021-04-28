"""Helper functions for ObjectIds and paths"""
from pathlib import PurePosixPath

from etl.file_processor_config import FileProcessorConfig
from etl.object_store.object_id import ObjectId


def _compute_config_path(config_object_id: ObjectId, *args) -> ObjectId:
    """Computes a bucket directory relative to a processor config path.

    :param config_file_name: The configuration file name.
    :return: The bucket path.
    """
    path = str(PurePosixPath(config_object_id.path).parent.joinpath(*args))
    return ObjectId(config_object_id.namespace, path)


def get_inbox_path(config_object_id: ObjectId, cfg: FileProcessorConfig, file_object_id: ObjectId = None) -> ObjectId:
    """Gets an ObjectId of the inbox directory for a given config or an object below it
    :param config_object_id: The ObjectId of the processor config file
    :param cfg: The deserialized processor config
    :param file_object_id: An optional object to locate in the directory
    """
    return (_compute_config_path(config_object_id, cfg.inbox_dir, filename(file_object_id))
            if file_object_id is not None
            else _compute_config_path(config_object_id, cfg.inbox_dir))


def get_processing_path(config_object_id: ObjectId, cfg: FileProcessorConfig, file_object_id: ObjectId = None) -> ObjectId:
    """Gets an ObjectId of the processing directory for a given config or an object below it
    :param config_object_id: The ObjectId of the processor config file
    :param cfg: The deserialized processor config
    :param file_object_id: An optional object to locate in the directory
    """
    return (_compute_config_path(config_object_id, cfg.processing_dir, filename(file_object_id))
            if file_object_id is not None
            else _compute_config_path(config_object_id, cfg.processing_dir))


def get_archive_path(config_object_id: ObjectId, cfg: FileProcessorConfig, file_object_id: ObjectId = None) -> ObjectId:
    """Gets an ObjectId of the archive directory for a given config or an object below it
    :param config_object_id: The ObjectId of the processor config file
    :param cfg: The deserialized processor config
    :param file_object_id: An optional object to locate in the directory
    """
    return (_compute_config_path(config_object_id, cfg.archive_dir, filename(file_object_id))
            if file_object_id is not None
            else _compute_config_path(config_object_id, cfg.archive_dir))


def get_error_path(config_object_id: ObjectId, cfg: FileProcessorConfig, file_object_id: ObjectId = None) -> ObjectId:
    """Gets an ObjectId of the error directory for a given config or an object below it
    :param config_object_id: The ObjectId of the processor config file
    :param cfg: The deserialized processor config
    :param file_object_id: An optional object to locate in the directory
    """
    return (_compute_config_path(config_object_id, cfg.error_dir, filename(file_object_id))
            if file_object_id is not None
            else _compute_config_path(config_object_id, cfg.error_dir))


def rename(object_id: ObjectId, new_filename: str) -> ObjectId:
    """Compute a sibling ObjectId in the same namespace and directory
    :param object_id: The starting point object
    :param new_filename: The name to replace the base object's with
    """
    path = str(PurePosixPath(object_id.path).parent.joinpath(new_filename))
    return ObjectId(object_id.namespace, path)


def parent(object_id: ObjectId) -> ObjectId:
    """Computes the directory containing the given object"""
    return ObjectId(object_id.namespace, str(PurePosixPath(object_id.path).parent))


def glob_matches(object_id: ObjectId, config_object_id: ObjectId, cfg: FileProcessorConfig) -> bool:
    """Checks if the configured glob pattern matches the object path relative to the config directory"""
    if object_id.namespace != config_object_id.namespace:
        return False

    try:
        return PurePosixPath(object_id.path).relative_to(parent(config_object_id).path).match(cfg.handled_file_glob)
    except ValueError:
        return False


def filename(object_id: ObjectId) -> str:
    """Gets just the leaf filename of the object"""
    return str(PurePosixPath(object_id.path).name)
