import requests
import time

def test_metrics_endpoint():
    # Wait for app to be ready
    for _ in range(20):  # 20 attempts
        try:
            r = requests.get('http://app:8080/metrics', timeout=2)
            if r.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(3)
    else:
        raise RuntimeError("App did not become ready in time")

    # Now test the metrics endpoint
    assert r.status_code == 200
    assert 'http_requests_total' in r.text
