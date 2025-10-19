import os
import requests

# Use environment variable (fallback to localhost)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

def test_metrics_endpoint():
    r = requests.get(f"{BASE_URL}/metrics", timeout=5)
    assert r.status_code == 200
    assert 'http_requests_total' in r.text
