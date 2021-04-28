# pylint: skip-file
import os
from types import SimpleNamespace

from etl import path_helpers
from etl.object_store.object_id import ObjectId

NAMESPACE = "test_namespace"

def get_config():
    cfg = SimpleNamespace()
    cfg.enabled = True
    cfg.handled_file_glob = "*_test.tsv"
    cfg.inbox_dir = "01_inbox"
    cfg.processing_dir = "02_processing"
    cfg.archive_dir = "03_archive"
    cfg.error_dir = "04_failed"
    return cfg
    
def test_get_inbox_path():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    cfg = get_config()
    actual = path_helpers.get_inbox_path(toml_id, cfg, ObjectId(NAMESPACE, 'dir/data.tsv'))
    assert '/tests/01_inbox/data.tsv' == actual.path
    assert NAMESPACE == actual.namespace

    actual = path_helpers.get_inbox_path(toml_id, cfg)
    assert '/tests/01_inbox' == actual.path
    assert NAMESPACE == actual.namespace

def test_get_processing_path():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    cfg = get_config()
    actual = path_helpers.get_processing_path(toml_id, cfg, ObjectId(NAMESPACE, 'dir/data.tsv'))
    assert '/tests/02_processing/data.tsv' == actual.path
    assert NAMESPACE == actual.namespace

    actual = path_helpers.get_processing_path(toml_id, cfg)
    assert '/tests/02_processing' == actual.path
    assert NAMESPACE == actual.namespace

def test_get_archive_path():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    cfg = get_config()
    actual = path_helpers.get_archive_path(toml_id, cfg, ObjectId(NAMESPACE, 'dir/data.tsv'))
    assert '/tests/03_archive/data.tsv' == actual.path
    assert NAMESPACE == actual.namespace

    actual = path_helpers.get_archive_path(toml_id, cfg)
    assert '/tests/03_archive' == actual.path
    assert NAMESPACE == actual.namespace

def test_get_error_path():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    cfg = get_config()
    actual = path_helpers.get_error_path(toml_id, cfg, ObjectId(NAMESPACE, 'dir/data.tsv'))
    assert '/tests/04_failed/data.tsv' == actual.path
    assert NAMESPACE == actual.namespace

    actual = path_helpers.get_error_path(toml_id, cfg)
    assert '/tests/04_failed' == actual.path
    assert NAMESPACE == actual.namespace

def test_rename():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    actual = path_helpers.rename(toml_id, 'expected.toml')
    assert '/tests/expected.toml' == actual.path
    assert NAMESPACE == actual.namespace

def test_parent():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    actual = path_helpers.parent(toml_id)
    assert '/tests' == actual.path
    assert NAMESPACE == actual.namespace

def test_glob_matches():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    cfg = get_config()

    assert path_helpers.glob_matches(ObjectId(NAMESPACE, '/tests/01_inbox/data_test.tsv'), toml_id, cfg)
    assert not path_helpers.glob_matches(ObjectId('bad_ns', '/tests/01_inbox/data_test.tsv'), toml_id, cfg)
    assert not path_helpers.glob_matches(ObjectId(NAMESPACE, '/tests/01_inbox/data_test.bad'), toml_id, cfg)
    assert not path_helpers.glob_matches(ObjectId(NAMESPACE, '/01_inbox/data_test.tsv'), toml_id, cfg)

def test_filename():
    toml_id = ObjectId(NAMESPACE, '/tests/test_config.toml')
    actual = path_helpers.filename(toml_id)
    assert 'test_config.toml' == actual
