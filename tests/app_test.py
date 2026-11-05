import sqlite3
from contextlib import closing

import pytest

from project.app import app, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Give each test its own empty database and application settings."""
    monkeypatch.setitem(app.config, "DATABASE", tmp_path / "test.db")
    monkeypatch.setitem(app.config, "TESTING", True)
    init_db()
    with app.test_client() as client:
        yield client


def login(client, username="admin", password="admin"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_database(client):
    database = app.config["DATABASE"]
    assert database.is_file()
    with closing(sqlite3.connect(database)) as connection:
        columns = connection.execute("PRAGMA table_info(entries)").fetchall()
        assert [column[1] for column in columns] == ["id", "title", "text"]
        assert connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0


def test_empty_db(client):
    response = client.get("/")
    assert b"No entries yet. Add some!" in response.data


def test_login_logout(client):
    assert client.get("/login").status_code == 200
    response = login(client)
    assert b"You were logged in" in response.data
    with client.session_transaction() as session:
        assert session["logged_in"] is True
    response = client.get("/logout", follow_redirects=True)
    assert b"You were logged out" in response.data
    with client.session_transaction() as session:
        assert "logged_in" not in session
    assert b"Invalid username" in login(client, username="wrong").data
    assert b"Invalid password" in login(client, password="wrong").data
    with client.session_transaction() as session:
        assert "logged_in" not in session


def test_messages(client):
    login(client)
    response = client.post(
        "/add",
        data={"title": "<Hello>", "text": "<strong>HTML</strong> allowed here"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"New entry was successfully posted" in response.data
    assert b"No entries yet. Add some!" not in response.data
    assert b"&lt;Hello&gt;" in response.data
    assert b"<strong>HTML</strong> allowed here" in response.data
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        assert connection.execute("SELECT title, text FROM entries").fetchall() == [
            ("<Hello>", "<strong>HTML</strong> allowed here")
        ]
    # A later request must also show the saved post.
    assert b"&lt;Hello&gt;" in client.get("/").data


def test_add_requires_login(client):
    response = client.post("/add", data={"title": "Blocked", "text": "Blocked"})
    assert response.status_code == 401
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        assert connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0


def test_delete_message(client):
    """Deleting a saved post removes it while preserving other posts."""
    login(client)
    for title in ("Delete me", "Keep me"):
        client.post("/add", data={"title": title, "text": "Example body"})
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        post_id = connection.execute(
            "SELECT id FROM entries WHERE title = ?", ("Delete me",)
        ).fetchone()[0]

    response = client.get(f"/delete/{post_id}")

    assert response.status_code == 200
    assert response.get_json()["status"] == 1
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        assert connection.execute("SELECT title FROM entries").fetchall() == [("Keep me",)]
    page = client.get("/").data
    assert b"Delete me" not in page
    assert b"Keep me" in page
