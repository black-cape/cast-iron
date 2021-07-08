hello# Cast Iron

The platform-agnostic data storage and ETL system leveraging MinIO and other tools to enable mission end states.

This repository contains the docker-compose recipe for staring up the backbone of Cast-Iron as well as the Cast-Iron Worker. 

Main Parts of the system include:
* Object Storage ([AWS S3], [MinIO], etc.)
* Message Queue ([Kafka], [Nats], etc.)
* Worker ([Celery], [Faust], etc.)
* ETL (Bash Scripts, Python)


## Getting Started

* Install [Docker]
* Create a startup script within your existing project that you would like to use Cast-Iron with. 
  See `cast-iron-recipe-postgres` for an example of this.   
* Clone this repository as a submodule within your existing repository with 
  `git submodule add git@github.com:black-cape/cast-iron-docker-compose.git`
  

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
