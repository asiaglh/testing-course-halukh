"""One PostgreSQL container per session and isolated transactions per test."""

import psycopg
import pytest
from testcontainers.community.postgres import PostgresContainer

from student_portal.repository import StudentRepository


@pytest.fixture(scope="session")
def database_url():
    with PostgresContainer("postgres:18-alpine", driver=None) as container:
        yield container.get_connection_url()


@pytest.fixture
def repository(database_url):
    with (
        psycopg.connect(database_url) as connection,
        connection.transaction(force_rollback=True),
    ):
        repo = StudentRepository(connection)
        repo.create_schema()
        yield repo
