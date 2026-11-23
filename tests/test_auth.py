"""FR-01, FR-02, FR-03: registration, sign in/out, password change."""
from conftest import csrf, login, register


def test_register_creates_account(client):
    res = register(client)
    assert res.status_code == 200
    assert b"Account created" in res.data


def test_register_rejects_duplicate_email(client):
    register(client)
    res = register(client)
    assert b"already registered" in res.data


def test_register_rejects_short_password(client):
    res = register(client, password="short")
    assert b"at least 8 characters" in res.data


def test_login_logout_flow(client):
    register(client)
    res = login(client)
    assert b"Daily summary" in res.data

    token = csrf(client, "/dashboard")
    res = client.post("/logout", data={"csrf_token": token},
                      follow_redirects=True)
    assert b"Sign in" in res.data

    # After sign-out the dashboard asks for authentication again.
    res = client.get("/dashboard")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_login_rejects_wrong_password(client):
    register(client)
    res = login(client, password="wrongpass1")
    assert b"Invalid email or password" in res.data


def test_change_password_requires_current(client):
    register(client)
    login(client)
    token = csrf(client, "/password/change")
    res = client.post("/password/change", data={
        "csrf_token": token,
        "current_password": "wrongpass1",
        "new_password": "newpassword1",
        "confirm": "newpassword1",
    }, follow_redirects=True)
    assert b"Current password is wrong" in res.data


def test_change_password_works(client):
    register(client)
    login(client)
    token = csrf(client, "/password/change")
    res = client.post("/password/change", data={
        "csrf_token": token,
        "current_password": "password123",
        "new_password": "newpassword1",
        "confirm": "newpassword1",
    }, follow_redirects=True)
    assert b"Password changed" in res.data
