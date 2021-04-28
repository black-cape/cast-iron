"""Handles parsing and validating ETL processor configs."""
import os
from functools import partial
from importlib import import_module
from inspect import isclass
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, Field, root_validator, validator
from toml import loads


class PythonProcessorConfig(BaseModel):
    """Configuration for Cast Iron to load some Python code available in the environment to process data"""
    worker_class: Optional[str] = Field(
        default=None,
        title='Worker Class',
        description='The absolute import path to a class that will be instantiated and used for data processing.'
    )
    worker_setup_method: Optional[str] = Field(
        default=None,
        title='Setup Method',
        description='The member method of the worker class to perform a pre-requisites for executing the run method. '
                    'This config is only used if the worker class is defined and the method will be invoked with the '
                    'named arguments.'
    )
    worker_run_method: str = Field(
        title='Run Method',
        description='The method that will be invoked to process incoming data. This method should expect a path to the '
                    'data file as the first argument. If the worker class is defined then this method should be a '
                    'member of the class, otherwise this should be the absolute import path.'
    )
    supports_pizza_tracker: Optional[bool] = Field(
        default=False,
        title='Supports Pizza Tracker',
        description=(
            'A flag to signal that the run method supports the `pizza_tracker` argument where the value is '
            'a path to a file.'
        )
    )
    supports_metadata: Optional[bool] = Field(
        default=False,
        title='Supports File Metadata',
        description=(
            'A flag to signal that the run method supports the `file_metadata` argument where the value is '
            'a dictionary containing metadata of the file from the object store.'
        )
    )
    static_kwargs: Optional[dict] = Field(
        default=None,
        title='Static Named Arguments',
        description='A map of named arguments to pass into the setup method or run method'
    )
    environment_kwargs: Optional[dict] = Field(
        default=None,
        title='Environment Named Arguments',
        description='A map of named arguments to the environment variables that hold their values. '
                    'This map will be used to generate additional named arguments to pass into the '
                    'setup method or run method'
    )

    @validator('worker_run_method')
    def ensure_run_method(cls, val: str) -> str:
        """Make sure the incoming values for the config has the worker_run_method set."""
        # Validators are a class method
        # pylint: disable=no-self-argument, no-self-use
        if not val:
            raise ValueError('The worker_run_method is not defined.')
        return val


class FileProcessorConfig(BaseModel):
    """An ETL processor configuration."""
    enabled: bool
    handled_file_glob: str
    inbox_dir: str
    processing_dir: str
    archive_dir: str
    error_dir: str
    save_error_log: bool
    # One of the following must be set in order to process incoming files
    shell: Optional[str] = None
    python: Optional[PythonProcessorConfig] = None

    @root_validator
    def ensure_exec(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure that either the shell or python values are provided."""
        # Validators are a class method
        # pylint: disable=no-self-argument, no-self-use
        if not values.get('shell') and not values.get('python'):
            raise ValueError('shell or python must be set')

        return values


def try_loads(file_contents: str) -> FileProcessorConfig:
    """Attempts to parse a TOML configuration file. Raises a ValueError on failure.

    :param file_contents: String to parse.
    :return: The Processor Config.
    """
    try:
        toml = loads(file_contents)
        cfg = toml.get('castiron', {}).get('etl', {})
        return FileProcessorConfig(**cfg)
    except Exception as ex:
        raise ValueError(ex)


def load_member(import_path: str, expect_class: bool = False) -> Any:
    """Load a member of a module using an absolute import path.

    :param import_path: The absolute import path for the member (i.e. package.module.member)
    :param expect_class: If the member is expected to be a class or not.
    :returns: The class, method, or variable from the import path.
    :raises ValueError: If a class was expected but the member was something else.
    """
    package, member = import_path.rsplit('.', 1)
    imported_package = import_module(package)
    member = getattr(imported_package, member)
    if expect_class and not isclass(member):
        raise ValueError(f'Member {member} of package {package} is not a class.')
    return member


def load_python_processor(config: PythonProcessorConfig) -> Callable:
    """Parse the Python processor config and return a callable to process the data.

    :param config: The configuration to process and load the necessary class and method.
    :returns: A callable that can be used to process data.
    """
    # Load the worker class and instantiate it if is not None
    worker = load_member(config.worker_class, expect_class=True)() if config.worker_class else None

    # Setup the static kwargs from the configs and combine them with the environment (dynamic) kwargs to
    # create the partial method
    kwargs = config.static_kwargs or {}
    if config.environment_kwargs:
        # This will overwrite static kwargs if they share the same key.
        kwargs.update(
            {
                argument: os.environ.get(env_var)
                for argument, env_var in config.environment_kwargs.items()
                if os.environ.get(env_var) is not None
            }
        )

    # If there is a worker and a setup method then invoke the setup with the named arguments
    # and return the run method
    # If there is a worker and no setup method then return a partial of the run method
    # If there is no worker then load the method dynamically
    if worker and config.worker_setup_method:
        setup = getattr(worker, config.worker_setup_method)
        setup(**kwargs)
        run = getattr(worker, config.worker_run_method)
    else:
        run = getattr(worker, config.worker_run_method) if worker else load_member(config.worker_run_method)
        run = partial(run, **kwargs)

    return run
