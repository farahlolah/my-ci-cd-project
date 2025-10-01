import sys
import os
import pytest

# Dynamically add the src folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app  


@pytest.fixture
def client():
    with app.test_client() as c:
        yield c

def test_root(client):
    rv = client.get('/')
    assert rv.status_code == 200
    json = rv.get_json()
    assert json['message'].startswith("Hello")
