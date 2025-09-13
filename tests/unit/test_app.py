import pytest
from src.app import app

@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

def test_root(client):
    rv = client.get('/')
    assert rv.status_code == 200
    json = rv.get_json()
    assert json['message'].startswith("Hello")
