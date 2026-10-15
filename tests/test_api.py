def test_root_endpoint(client):
    """Test / root endpoint returns welcome message and endpoint index."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert "endpoints" in data
    assert "/health" in data["endpoints"].values()
    assert "/healthz" in data["endpoints"].values()
    assert "/ready" in data["endpoints"].values()


def test_ping_endpoint(client):
    """Test /api/v1/ping returns pong."""
    response = client.get("/api/v1/ping")
    assert response.status_code == 200

    data = response.get_json()
    assert data["message"] == "pong"


def test_info_endpoint(client):
    """Test /api/v1/info returns system and app metadata."""
    response = client.get("/api/v1/info")
    assert response.status_code == 200

    data = response.get_json()
    assert "app_name" in data
    assert "version" in data
    assert "environment" in data
    assert "python_version" in data


def test_404_handler(client):
    """Test non-existent route returns 404 JSON response."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Not Found"


def test_500_handler(app, client):
    """Test 500 internal server error handler."""
    from flask import abort

    @app.route("/error-500-trigger")
    def trigger_error():
        abort(500)

    response = client.get("/error-500-trigger")
    assert response.status_code == 500

    data = response.get_json()
    assert data["error"] == "Internal Server Error"
    assert "unexpected error" in data["message"]


