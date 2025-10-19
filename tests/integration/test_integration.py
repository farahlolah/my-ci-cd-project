import requests

def test_metrics_endpoint():
    r = requests.get('http://host.docker.internal:8081/metrics', timeout=5)
    assert r.status_code == 200
    assert 'http_requests_total' in r.text
