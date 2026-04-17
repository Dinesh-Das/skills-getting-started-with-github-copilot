import pytest
from httpx import AsyncClient
from src.app import app, activities
from fastapi import status
import copy

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset the in-memory activities before each test
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(orig))

@pytest.mark.asyncio
async def test_get_activities():
    # Arrange: (nothing to set up, uses default data)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.get("/activities")
        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert "Chess Club" in data
        assert isinstance(data["Chess Club"], dict)

@pytest.mark.asyncio
async def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.post(f"/activities/{activity}/signup", params={"email": email})
        # Assert
        assert resp.status_code == 200
        assert email in activities[activity]["participants"]

@pytest.mark.asyncio
async def test_signup_already_registered():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    activity = "Chess Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.post(f"/activities/{activity}/signup", params={"email": email})
        # Assert
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Student already signed up"

@pytest.mark.asyncio
async def test_signup_activity_not_found():
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Nonexistent Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.post(f"/activities/{activity}/signup", params={"email": email})
        # Assert
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Activity not found"

@pytest.mark.asyncio
async def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.delete(f"/activities/{activity}/unregister", params={"email": email})
        # Assert
        assert resp.status_code == 200
        assert email not in activities[activity]["participants"]

@pytest.mark.asyncio
async def test_unregister_not_found():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.delete(f"/activities/{activity}/unregister", params={"email": email})
        # Assert
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Participant not found"
