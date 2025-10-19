import requests

def test_metrics_endpoint():
    # Use service name and internal container port
    r = requests.get('http://app:8081/metrics', timeout=5)
    assert r.status_code == 200
    assert 'http_requests_total' in r.text
