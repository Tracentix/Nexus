"""FR-04, FR-06, FR-12, FR-15: ownership rules, goals, measurements."""
from datetime import date

from conftest import csrf, login, register


def _two_users(client_a, client_b):
    register(client_a, email="a@example.com", name="User A")
    register(client_b, email="b@example.com", name="User B")
    login(client_a, email="a@example.com")
    login(client_b, email="b@example.com")


def _add_workout(client):
    token = csrf(client, "/workouts/new")
    client.post("/workouts/new", data={
        "csrf_token": token,
        "activity_type": "Running",
        "started_on": date.today().isoformat(),
        "duration_minutes": 20,
        "estimated_kcal": "",
        "notes": "",
    }, follow_redirects=True)


def test_owner_only_edit(client, app):
    # A second member must not touch another member's workout (FR-06).
    register(client, email="a@example.com", name="User A")
    login(client, email="a@example.com")
    _add_workout(client)
    other = app.test_client()
    register(other, email="b@example.com", name="User B")
    login(other, email="b@example.com")
    res = other.get("/workouts/1/edit")
    assert res.status_code in (403, 404)


def test_goal_lifecycle(client):
    register(client)
    login(client)
    token = csrf(client, "/goals/new")
    res = client.post("/goals/new", data={
        "csrf_token": token,
        "goal_type": "weight",
        "description": "Reach 75 kg",
        "target_value": "75",
        "target_date": "",
    }, follow_redirects=True)
    assert b"Goal created" in res.data

    token = csrf(client, "/goals")
    res = client.post("/goals/1/status", data={
        "csrf_token": token, "status": "completed",
    }, follow_redirects=True)
    assert b"marked as completed" in res.data
    # Completed goals leave the active list.
    assert b"<h2>Active</h2>\n<p class=\"empty\">" in res.data or \
           b"No active goals" in res.data


def test_goal_requires_description(client):
    register(client)
    login(client)
    token = csrf(client, "/goals/new")
    res = client.post("/goals/new", data={
        "csrf_token": token,
        "goal_type": "weight",
        "description": "",
        "target_value": "",
        "target_date": "",
    }, follow_redirects=True)
    assert b"Describe the goal" in res.data


def test_measurement_record_and_delete(client):
    register(client)
    login(client)
    token = csrf(client, "/measurements")
    res = client.post("/measurements", data={
        "csrf_token": token,
        "kind": "weight",
        "value": "82.5",
        "measured_on": date.today().isoformat(),
    }, follow_redirects=True)
    assert b"Measurement recorded" in res.data
    assert b"82.5" in res.data

    token = csrf(client, "/measurements")
    res = client.post("/measurements/1/delete", data={
        "csrf_token": token,
    }, follow_redirects=True)
    assert b"Measurement deleted" in res.data


def test_profile_edit_persists(client):
    register(client)
    login(client)
    token = csrf(client, "/profile/")
    res = client.post("/profile/", data={
        "csrf_token": token,
        "display_name": "New Name",
        "preferences": "morning runs",
        "daily_calorie_target": "2000",
    }, follow_redirects=True)
    assert b"Profile updated" in res.data
    res = client.get("/profile/")
    assert b"New Name" in res.data
    assert b"2000" in res.data


def test_protected_pages_require_login(client):
    for url in ("/dashboard", "/workouts", "/meals", "/goals",
                "/measurements", "/charts", "/profile/"):
        res = client.get(url)
        assert res.status_code == 302, url
