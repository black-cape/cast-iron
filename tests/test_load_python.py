from unittest import TestCase

from etl.file_processor_config import (PythonProcessorConfig,
                                       load_python_processor)


class TestLoadPythonprocessor(TestCase):
    """Test cases for the provider method."""
    def setUp(self) -> None:
        self.config = PythonProcessorConfig(worker_run_method='run')

    def test_load_with_class(self):
        """Validate a load with a class and no setup results in a partial method."""
        self.config.worker_class = 'tests.utils.DummyClass'
        self.config.static_kwargs = {'test': 1}

        loaded_callable = load_python_processor(self.config)
        self.assertTrue(callable(loaded_callable))
        self.assertEqual(loaded_callable.args, ())
        self.assertDictEqual(loaded_callable.keywords, {'test': 1})

    def test_load_with_setup(self):
        """Validate a load with setup results in just a callable."""
        self.config.worker_class = 'tests.utils.DummyClass'
        self.config.worker_setup_method = 'setup'
        self.config.static_kwargs = {'test': 1}

        loaded_callable = load_python_processor(self.config)
        self.assertTrue(callable(loaded_callable))
        self.assertIsNone(getattr(loaded_callable, 'args', None))

    def test_load_without_class(self):
        """Validate a load without a class."""
        self.config.worker_run_method = 'tests.utils.test_run'
        self.config.static_kwargs = {'test': 1}

        loaded_callable = load_python_processor(self.config)
        self.assertTrue(callable(loaded_callable))
        self.assertEqual(loaded_callable.args, ())
        self.assertEqual(loaded_callable.keywords, {'test': 1})
