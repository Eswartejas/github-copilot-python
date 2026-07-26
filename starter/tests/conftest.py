import pytest
from app import app as flask_app, CURRENT


@pytest.fixture
def client():
    """Create a Flask test client for the starter app."""
    flask_app.config['TESTING'] = True
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    with flask_app.test_client() as client:
        yield client
