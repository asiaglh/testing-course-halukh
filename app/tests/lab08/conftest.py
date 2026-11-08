"""Ізольований API-сервер і браузерні фікстури для ЛР 8."""

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

from .pages.login_page import LoginPage
from .pages.students_page import StudentsPage

DATA = Path(__file__).resolve().parents[2] / "data" / "group.json"
_counter = itertools.count(1)


def free_port() -> int:
    with socket.socket() as address:
        address.bind(("127.0.0.1", 0))
        return address.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    """Працювати з копією початкових даних, не змінюючи файл курсу."""
    data = tmp_path_factory.mktemp("lab08-data") / "group.json"
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
            raise RuntimeError("Сервер ЛР 8 не запустився")
        time.sleep(0.05)
    yield f"http://127.0.0.1:{server.config.port}"
    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture
def unique_email():
    return f"e2e{next(_counter)}@students.example.edu"


@pytest.fixture
def created_student(base_url, unique_email):
    """Нова картка для тесту оцінок, створена API від імені адміністратора."""
    with httpx.Client(
        base_url=base_url, headers={"Authorization": "Bearer admin-token"}
    ) as client:
        response = client.post(
            "/api/students",
            json={
                "last_name": "Дослідний",
                "first_name": "Студент",
                "email": unique_email,
            },
        )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def as_admin(page, base_url):
    LoginPage(page, base_url).open().login("admin-token")
    return StudentsPage(page).wait_loaded()


@pytest.fixture
def as_teacher(page, base_url):
    LoginPage(page, base_url).open().login("teacher-token")
    return StudentsPage(page).wait_loaded()
