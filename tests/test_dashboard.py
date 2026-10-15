def test_dashboard_page(client):
    """Test /dashboard endpoint returns HTTP 200 and renders HTML with expected components."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Verify Page Title & Headings
    assert "<title>DevOps Automation Platform</title>" in html
    assert "CORE PLATFORM" in html
    assert "INFRASTRUCTURE & OPS" in html

    # Verify All 7 Required Sidebar Navigation Sections
    assert "Overview" in html
    assert "CI/CD Pipeline" in html
    assert "Docker Containers" in html
    assert "Kubernetes" in html
    assert "Monitoring" in html
    assert "Security Scanning" in html
    assert "Infrastructure" in html

    # Verify Required Metric Cards
    assert "APPLICATION HEALTH" in html
    assert "PIPELINE STATUS" in html
    assert "DOCKER CONTAINER" in html
    assert "CPU UTILIZATION" in html
    assert "MEMORY UTILIZATION" in html

    # Verify Diagnostic Console and Deployments Table
    assert "Interactive API &amp; Probe Diagnostic Console" in html or "Interactive API & Probe Diagnostic Console" in html
    assert "Recent Deployment Activity" in html


def test_system_metrics_endpoint(client):
    """Test /api/v1/system/metrics returns valid live OS metrics structure."""
    response = client.get("/api/v1/system/metrics")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "online"

    # CPU checks
    assert "cpu" in data
    assert "cores" in data["cpu"]
    assert isinstance(data["cpu"]["cores"], int)
    assert data["cpu"]["cores"] >= 1
    assert "percent" in data["cpu"]
    assert "load_1m" in data["cpu"]

    # Memory checks
    assert "memory" in data
    assert "total_mb" in data["memory"]
    assert "used_mb" in data["memory"]
    assert "percent" in data["memory"]

    # Disk checks
    assert "disk" in data
    assert "total_gb" in data["disk"]
    assert "percent" in data["disk"]


def test_deployments_endpoint(client):
    """Test /api/v1/deployments returns deployment history or release milestones."""
    response = client.get("/api/v1/deployments")
    assert response.status_code == 200

    data = response.get_json()
    assert "deployments" in data
    assert isinstance(data["deployments"], list)
    assert len(data["deployments"]) > 0

    first_item = data["deployments"][0]
    assert "commit" in first_item
    assert "message" in first_item
    assert "author" in first_item
    assert "status" in first_item


def test_root_gui_redirect(client):
    """Test /?view=gui redirects to /dashboard."""
    response = client.get("/?view=gui")
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("Location", "")
