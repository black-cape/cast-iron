"""
The config module contains logic for loading, parsing, and formatting faust configuration.
"""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings derived from command line, environment variables, .env file or defaults """
    worker_name: str = 'cast-iron-faust'

    database_host: str = 'localhost'
    database_password: str = '12345678'  # Default for local debugging
    database_port: int = 5432
    database_user: str = 'castiron'
    database_table: str = 'castiron'

    kafka_broker: str = 'localhost:9092'
    kafka_minio_topic: str = 'minio'
    kafka_store_topic: str = 'postgres'
    kafka_pizza_tracker_topic: str = 'pizza-tracker'

    minio_etl_bucket: str = 'etl'
    minio_host: str = 'localhost:9000'
    minio_access_key: str = 'castiron'
    minio_secret_key: str = 'castiron'
    minio_secure: bool = False
    minio_notification_arn: str = 'arn:minio:sqs::docker:kafka'


settings = Settings()
