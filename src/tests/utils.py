import os

import docker


def set_test_env():
    os.environ["DB_USER"] = "user"
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_PASSWORD"] = "password"
    os.environ["DB_NAME"] = "test_db"
    os.environ["DB_PORT"] = "54329"


def run_db_container():
    client = docker.from_env()
    container = client.containers.run(
        image="postgres:16-alpine",
        name="postgres_test",
        detach=True,
        environment={
            "POSTGRES_USER": os.environ.get("DB_USER"),
            "POSTGRES_PASSWORD": os.environ.get("DB_PASSWORD"),
            "PGDATA": "/var/lib/postgresql/data",
            "POSTGRES_DB": os.environ.get("DB_NAME"),
        },
        remove=True,
        ports={"5432/tcp": os.environ.get("DB_PORT")},
        healthcheck={
            "test": [
                "CMD",
                "pg_isready",
                "-d",
                os.environ.get("DB_NAME"),
                "-U",
                os.environ.get("DB_USER")
            ],
            "interval": 1000000000,  # 1 second in nanoseconds
            "timeout": 1000000000,  # 1 second in nanoseconds
            "retries": 10,
        }
    )

    return container


def get_container_status(container_name):
    client = docker.from_env()
    status = client.api.inspect_container(container_name)['State']['Health']['Status']
    return status


def get_db_uri():
    uri = (
        f'postgresql+asyncpg://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWORD")}'
        f'@127.0.0.1:{os.environ.get("DB_PORT")}/test_db'
    )
    return uri
