"""FR-05..11, FR-13: workouts, meals, calorie target, daily summary."""
from datetime import date

from conftest import csrf, login, register


def _login(client):
    register(client)
    login(client)


def add_workout(client, duration=30, day=None, wtype="Running", kcal=""):
    token = csrf(client, "/workouts/new")
    return client.post("/workouts/new", data={
        "csrf_token": token,
        "activity_type": wtype,
        "started_on": day or date.today().isoformat(),
        "duration_minutes": duration,
        "estimated_kcal": kcal,
        "notes": "",
    }, follow_redirects=True)


def add_meal(client, food_id=1, quantity=2, day=None, label="lunch"):
    token = csrf(client, "/meals/new")
    return client.post("/meals/new", data={
        "csrf_token": token,
        "food_id": food_id,
        "meal_label": label,
        "quantity": quantity,
        "eaten_on": day or date.today().isoformat(),
    }, follow_redirects=True)


def test_record_workout(client):
    _login(client)
    res = add_workout(client, duration=45)
    assert b"Workout recorded" in res.data
    assert b"45 min" in res.data


def test_workout_rejects_zero_duration(client):
    _login(client)
    res = add_workout(client, duration=0)
    assert b"positive number of minutes" in res.data


def test_workout_rejects_future_date(client):
    _login(client)
    res = add_workout(client, day="2999-01-01")
    assert b"cannot be in the future" in res.data


def test_workout_history_filter(client):
    _login(client)
    add_workout(client, wtype="Running")
    add_workout(client, wtype="Swimming")
    res = client.get("/workouts?type=Swimming")
    assert b"Swimming" in res.data
    # The filtered table must not show the Running row (the word "Running"
    # still appears in the filter dropdown itself).
    assert b"<td>Running</td>" not in res.data


def test_meal_calorie_snapshot(client):
    _login(client)
    # Apple is 95 kcal per piece; 2 pieces must snapshot to 190 kcal.
    res = add_meal(client, food_id=1, quantity=2)
    assert b"190" in res.data


def test_inactive_food_cannot_be_logged(client):
    _login(client)
    res = add_meal(client, food_id=2)  # Old bread is inactive
    assert b"active food item" in res.data


def test_calorie_target_validation(client):
    _login(client)
    token = csrf(client, "/profile/")
    res = client.post("/profile/", data={
        "csrf_token": token,
        "display_name": "Test User",
        "preferences": "",
        "daily_calorie_target": "100",
    }, follow_redirects=True)
    assert b"between 500 and 10000" in res.data


def test_daily_summary_totals(client):
    _login(client)
    add_workout(client, duration=30)
    add_meal(client, food_id=1, quantity=2)
    res = client.get("/dashboard")
    assert b"30 min" in res.data
    assert b"190" in res.data  # meal total matches stored entries
