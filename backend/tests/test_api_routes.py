from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_nonexistent_complaint_returns_404():
    response = client.get("/api/complaints/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_and_get_complaint():
    payload = {
        "text": "Test complaint via API route for coverage testing purposes",
        "location": "Test City",
        "reporter_contact": None,
    }
    create_response = client.post("/api/complaints", json=payload)
    assert create_response.status_code == 201
    complaint_id = create_response.json()["id"]

    get_response = client.get(f"/api/complaints/{complaint_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == complaint_id


def test_list_complaints():
    response = client.get("/api/complaints")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()


def test_invalid_status_transition_returns_409():
    payload = {
        "text": "Another test complaint for status transition testing",
        "location": "Test City",
        "reporter_contact": None,
    }
    create_response = client.post("/api/complaints", json=payload)
    complaint_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/api/complaints/{complaint_id}/status", json={"status": "resolved"}
    )
    assert patch_response.status_code == 409


def test_stats_endpoint_has_cache_header():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert "x-cache" in response.headers
