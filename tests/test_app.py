from typing import Dict, Any

from fastapi.testclient import TestClient

from src.app import activities


def test_root_redirects_to_static_index(client: TestClient) -> None:
    # Arrange
    # (client fixture is provided)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client: TestClient) -> None:
    # Arrange
    # (baseline activities are provided by the reset_activities fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()

    # Check that at least a couple of known activities exist
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check that each activity has the expected fields
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


def test_signup_adds_new_participant(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert new_email in body.get("message", "")
    assert activity_name in body.get("message", "")

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    updated = activities_response.json()[activity_name]
    assert new_email in updated["participants"]


def test_signup_fails_for_nonexistent_activity(client: TestClient) -> None:
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert body.get("detail") == "Activity not found"


def test_signup_fails_when_already_signed_up(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body.get("detail") == "Student already signed up for this activity"


def test_signup_fails_when_activity_full(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{i}@mergington.edu" for i in range(activity["max_participants"])
    ]
    extra_email = "extra@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": extra_email},
    )

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body.get("detail") == "Activity is full"


def test_unregister_removes_participant(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert email in body.get("message", "")

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    updated = activities_response.json()[activity_name]
    assert email not in updated["participants"]


def test_unregister_fails_for_nonexistent_activity(client: TestClient) -> None:
    # Arrange
    activity_name = "Made Up Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert body.get("detail") == "Activity not found"


def test_unregister_fails_when_not_registered(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert body.get("detail") == "Student is not registered for this activity"
