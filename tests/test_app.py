import copy

import pytest
from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activity_state():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_adds_participant():
    activity_name = "Math Club"
    student_email = "tester@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {student_email} for {activity_name}"
    }
    assert student_email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "tester@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant_returns_400():
    activity_name = "Math Club"
    student_email = "duplicate@mergington.edu"

    first_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"
