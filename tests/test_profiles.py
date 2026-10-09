import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_cache_profile(async_client: AsyncClient):
    payload = {
        "first_name": "Devak",
        "last_name": "Kumar",
        "email": "devak@example.com",
        "phone": "+1234567890",
        "location": "San Francisco, CA",
        "summary": "Experienced Full Stack Software Engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Vue.js"],
        "work_authorization": "Yes",
        "requires_sponsorship": "No",
        "desired_salary": "140000",
        "notice_period": "14 days"
    }

    # 1. Create Profile via API
    response = await async_client.post("/api/v1/profiles/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    profile_id = data["data"]["id"]

    # 2. Get Active Profile from Redis Cache
    active_resp = await async_client.get("/api/v1/profiles/active")
    assert active_resp.status_code == 200
    active_data = active_resp.json()["data"]
    assert active_data["email"] == "devak@example.com"
    assert active_data["first_name"] == "Devak"
    assert "FastAPI" in active_data["skills"]

    # 3. Get Specific Profile by ID (hits Redis cache)
    get_resp = await async_client.get(f"/api/v1/profiles/{profile_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()["data"]
    assert get_data["id"] == profile_id
    assert get_data["location"] == "San Francisco, CA"
