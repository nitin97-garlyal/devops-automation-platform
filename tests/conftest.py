import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure an isolated Flask app instance for tests."""
    application = create_app(config_name="testing")
    yield application


@pytest.fixture
def client(app):
    """A test client for the app to make HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for testing Flask commands."""
    return app.test_cli_runner()
