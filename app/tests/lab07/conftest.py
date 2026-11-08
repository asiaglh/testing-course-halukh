"""Isolated HTTP server and clients for Lab 7 black-box API tests."""

import itertools
import shutil
import socket
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn

from student_portal.api import create_app
from student_portal.storage import load_group

DATA = Path(__file__).resolve().parents[2] / "data" / "group.json"
_counter = itertools.count(1)


def free_port() -> int:
    with socket.socket() as address:
        address.bind(("127.0.0.1", 0))
        return address.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    """Start one server on a copy of the sample group, leaving the source intact."""
    data = tmp_path_factory.mktemp("lab07-data") / "group.json"
    shutil.copy(DATA, data)
    server = uvicorn.Server(
        uvicorn.Config(
            create_app(load_group(data)),
            host="127.0.0.1",
            port=free_port(),
            log_level="warning",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started:
        if not thread.is_alive() or time.monotonic() >= deadline:
            raise RuntimeError("Lab 7 API server did not start")
        time.sleep(0.05)
    yield f"http://127.0.0.1:{server.config.port}"
    server.should_exit = True
    thread.join(timeout=10)


def client_for(base_url: str, token: str | None) -> httpx.Client:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.Client(base_url=base_url, headers=headers, timeout=5)


@pytest.fixture
def admin(base_url):
    with client_for(base_url, "admin-token") as client:
        yield client


@pytest.fixture
def teacher(base_url):
    with client_for(base_url, "teacher-token") as client:
        yield client


@pytest.fixture
def anonymous(base_url):
    with client_for(base_url, None) as client:
        yield client


@pytest.fixture
def new_student():
    number = next(_counter)
    return {
        "first_name": "Тарас",
        "last_name": "Гнатюк",
        "email": f"t.hnatiuk{number}@students.example.edu",
    }


@pytest.fixture
def created(admin, new_student):
    response = admin.post("/api/students", json=new_student)
    assert response.status_code == 201
    return response.headers["Location"], response.json()
