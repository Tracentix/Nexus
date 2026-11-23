import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import FoodItem  # noqa: E402


class TestConfig:
    SECRET_KEY = "test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIN_CALORIE_TARGET = 500
    MAX_CALORIE_TARGET = 10000
    RESET_TOKEN_MINUTES = 30
    MAIL_DELIVERY = "console"


@pytest.fixture()
def app():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    class Cfg(TestConfig):
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + path

    app = create_app(Cfg)
    with app.app_context():
        db.create_all()
        db.session.add(FoodItem(name="Apple", serving_unit="piece",
                                calories_per_unit=95, is_active=True))
        db.session.add(FoodItem(name="Old bread", serving_unit="loaf",
                                calories_per_unit=160, is_active=False))
        db.session.commit()
    yield app
    os.unlink(path)


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, url="/login"):
    """Fetch a page and pull the CSRF token out of its form."""
    html = client.get(url).data.decode()
    marker = 'name="csrf_token" value="'
    return html.split(marker)[1].split('"')[0]


def register(client, email="user@example.com", password="password123",
             name="Test User"):
    return client.post("/register", data={
        "csrf_token": csrf(client, "/register"),
        "display_name": name,
        "email": email,
        "password": password,
        "confirm": password,
    }, follow_redirects=True)


def login(client, email="user@example.com", password="password123"):
    return client.post("/login", data={
        "csrf_token": csrf(client),
        "email": email,
        "password": password,
    }, follow_redirects=True)
