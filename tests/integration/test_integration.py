import requests

def test_metrics_endpoint():
    r = requests.get('http://app:8080/metrics', timeout=5)
    assert r.status_code == 200
    assert 'http_requests_total' in r.text
