# pylint: skip-file
import os

from etl.file_processor_config import PythonProcessorConfig, try_loads


def test_try_loads():
    path = os.path.join(os.path.dirname(__file__), 'test_config.toml')
    with open(path, 'r') as f:
        data = f.read()
    actual = try_loads(data)
    assert True == actual.enabled
    assert "*_test.tsv" == actual.handled_file_glob
    assert "01_inbox" == actual.inbox_dir
    assert "02_processing" == actual.processing_dir
    assert "03_archive" == actual.archive_dir
    assert "04_failed" == actual.error_dir
    assert False == actual.save_error_log
    assert "shell" == actual.shell.strip()

    caught_value_error = False
    try:
        try_loads('')
    except ValueError:
        caught_value_error = True
        pass
    assert caught_value_error


def test_python_try_loads():
    path = os.path.join(os.path.dirname(__file__), 'test_python_config.toml')
    with open(path, 'r') as f:
        data = f.read()
    actual = try_loads(data)
    assert True == actual.enabled
    assert "*_test.tsv" == actual.handled_file_glob
    assert "01_inbox" == actual.inbox_dir
    assert "02_processing" == actual.processing_dir
    assert "03_archive" == actual.archive_dir
    assert "04_failed" == actual.error_dir
    assert actual.shell is None
    assert actual.python is not None and isinstance(actual.python, PythonProcessorConfig)

    caught_value_error = False
    try:
        try_loads('')
    except ValueError:
        caught_value_error = True
        pass
    assert caught_value_error
