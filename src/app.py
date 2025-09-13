from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUESTS = Counter('http_requests_total', 'Total HTTP Requests', ['method','endpoint'])

@app.route('/')
def hello():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    return jsonify(message="Hello from MyApp"), 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
