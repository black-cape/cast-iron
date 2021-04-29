FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Using a different directory than /usr/src/app to allow volume mounting of code to /usr/src/app for local development
WORKDIR /opt/setup

RUN apt-get update && \
  apt-get -y install gcc g++ && \
  python -m pip install --upgrade pip && \
  pip install --upgrade poetry
COPY . /opt/setup
RUN poetry install --no-dev --no-interaction --no-ansi

FROM ghcr.io/black-cape/cast-iron/worker:latest

RUN apt-get update && \
  apt-get -y install gcc g++

# Copy the virtual environment from the first stage so we can set the Python path to it's packages
# avoiding the need to install any of the dependencies
COPY --from=0 /opt/setup/.venv /opt/setup/.venv
# Set additional Python paths to expose libraries installed in previous stages
ENV PYTHONPATH="/usr/local/lib/python3.8/site-packages/:/opt/setup/.venv/lib/python3.8/site-packages:$PYTHONPATH"
ENV PATH="$PATH:/opt/setup/.venv/bin"

ADD modules /app/modules
