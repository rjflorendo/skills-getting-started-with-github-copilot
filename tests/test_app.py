import copy
import pytest
from fastapi.testclient import TestClient

from app import app, activities

# keep a deep copy of the initial state so tests can reset the in-memory db
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset the shared activities dict before each test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_initial_data():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == INITIAL_ACTIVITIES


def test_successful_signup_adds_participant():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json() == {"message": f"Signed up {email} for {activity}"}


def test_signup_duplicate_email_returns_400():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    client = TestClient(app)
    activity = "Nonexistent Club"
    email = "foo@bar.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": participant})

    # Assert
    assert response.status_code == 200
    assert participant not in activities[activity]["participants"]
    assert response.json() == {"message": f"Removed {participant} from {activity}"}


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "not@there.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_remove_from_nonexistent_activity_returns_404():
    # Arrange
    client = TestClient(app)
    activity = "NoClub"
    email = "foo@bar.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
