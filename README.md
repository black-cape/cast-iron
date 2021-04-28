# Cast Iron

The platform-agnostic data storage and ETL system leveraging MinIO and other tools to enable mission endstates.

## Basics

This project provides an example environment using [MinIO] to create a basic, cloud-agnostic ETL system.

Main Parts of the system include:
* Object Storage ([AWS S3], [MinIO], etc.)
* Message Queue ([Kafka], [Nats], etc.)
* Worker ([Celery], [Faust], etc.)
* ETL (Bash Scripts, Python)
* Database ([MS SQL], [MySQL], [PostgreSQL], [SQLite], etc.)

## Architecture

![architecture](diagrams/cast-iron-architecture-diagram.png)

## Getting Started

* Install [Docker]
* Run the docker compose
```bash
$ docker-compose up
```

Once started, the following areas are accessible:
* MinIO at localhost:9000
* PostgreSQL
    * User: castiron
    * Password: castiron
    * Host: localhost
    * Port: 5432
    * Database: castiron


[AWS S3]: https://aws.amazon.com/s3/
[Celery]: https://docs.celeryproject.org/en/stable/index.html
[Docker]: https://www.docker.com/
[Faust]: https://faust.readthedocs.io/en/latest/index.html
[Kafka]: https://kafka.apache.org/
[MinIO]: https://min.io/
[MySQL]: https://www.mysql.com/
[Nats]: https://nats.io/
[PostgreSQL]: https://www.postgresql.org/
[SQLite]: https://www.sqlite.org/index.html
[MS SQL]: https://www.microsoft.com/en-us/sql-server
