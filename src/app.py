from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, Gauge

app = Flask(__name__)

# Metrics
REQUESTS = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request latency in seconds', 
    ['method', 'endpoint']
)

APP_UP = Gauge(
    'app_up', 
    'Application uptime status'
)

# Mark app as up
APP_UP.set(1)

# Example route
@app.route('/')
def hello():
    with REQUEST_LATENCY.labels(method='GET', endpoint='/').time():
        REQUESTS.labels(method='GET', endpoint='/').inc()
        return jsonify(message="Hello from MyApp"), 200

# Example route for testing POST
@app.route('/test', methods=['POST'])
def test():
    with REQUEST_LATENCY.labels(method='POST', endpoint='/test').time():
        REQUESTS.labels(method='POST', endpoint='/test').inc()
        return jsonify(message="POST request received"), 200

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=8080)
