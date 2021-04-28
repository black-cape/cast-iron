# Faust Worker Example

## Getting Started

The Faust Worker example leverages several Python libraries to accomplish the ETL process.
* [Faust](https://faust.readthedocs.io/en/latest/index.html)
* [Kafka](https://github.com/dpkp/kafka-python)
* [Minio](https://docs.min.io/docs/python-client-api-reference.html)
* [Pydantic](https://pydantic-docs.helpmanual.io/)
* [Toml](https://github.com/uiri/toml)
* [urllib3](https://urllib3.readthedocs.io/en/latest/)

## Installing Dependencies

* Install Python 3.8, preferably using [Pyenv](https://github.com/pyenv/pyenv)
```bash
$ pyenv install
```
* This project utilizes [Poetry](https://python-poetry.org/docs/#installation) for managing python dependencies.
```bash
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```
* Install dependencies
```bash
$ poetry install
```

## Start the Worker

1. Add `127.0.0.1 kafka` entry to your /etc/hosts file
1. Start the Faust ETL worker
    * Locally
    ```
    $ poetry shell
    $ faust -A python_worker.etl worker -l info
    ```
      - To run with a debugger use `python worker.py`
    * Docker
    ```
    $ docker-compose up --build
    ```

## Utlize the ETL

With the docker containers running and the worker running in either a container or locally
1. Navigate to MinIO `http://localhost:9000`
1. Add `example_config.toml` to the `etl` bucket
1. Refresh the page to verify that additional etl buckets are created
1. Navigate into `01_inbox`
1. Add `data/data_test.tsv`
1. TSV should be ETL-ed
1. TSV moves to the `archive_dir` bucket
1. Data inserted into Postgres

## Technology

### Toml

[Toml](https://en.wikipedia.org/wiki/TOML) is used to create configuration files that can be used to tell the worker how
to ETL a given file.

An example configuration file can be seen in the `example_config.toml` and the `example_python_config.toml`.

### MinIO

Several buckets are used as stages in the ETL process. These buckets are defined in the toml config file. The buckets
are created i
* `inbox_dir`
* `processing_dir`
* `archive_dir`
* `error_dir`

### Settings

The `Settings` class allows for the usage of environment variables or a `.env` file to supply the appropriate arguments
based on its inheritance of Pyandatic's `BaseSettings` class. Additional details on how `BaseSettings` works can be
found in the Pydantic [documentation](https://pydantic-docs.helpmanual.io/usage/settings/).
