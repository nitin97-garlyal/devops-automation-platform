import json


def test_health_endpoint(client):
    """Test /health endpoint returns 200 and valid JSON with required keys."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)
    assert "timestamp" in data


def test_liveness_probe(client):
    """Test /healthz Kubernetes liveness probe returns 200 alive."""
    response = client.get("/healthz")
    assert response.status_code == 200

    data = response.get_json()
    assert data == {"status": "alive"}


def test_readiness_probe(client):
    """Test /ready Kubernetes readiness probe returns 200 ready."""
    response = client.get("/ready")
    assert response.status_code == 200

    data = response.get_json()
    assert data == {"status": "ready"}
