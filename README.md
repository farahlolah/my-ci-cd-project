# Lightweight CI/CD Pipeline for Small Teams

This project demonstrates a lightweight CI/CD pipeline for a small Flask application using:
- GitHub (source control)
- Jenkins (CI/CD orchestration)
- Docker + Docker Compose (packaging & deployment)
- Prometheus + Grafana (monitoring)

## Project structure
- `src/` - application code (Flask app)
- `tests/` - unit & integration tests
- `Dockerfile` - builds app container
- `Jenkinsfile` - defines pipeline stages
- `docker-compose.staging.yml` - staging deployment
- `docker-compose.prod.yml` - production deployment with monitoring
- `prometheus.yml` - Prometheus scrape config

## Quick start (local)
```bash
# Run app locally
pip install -r requirements.txt
python src/app.py

# Staging environment
docker-compose -f docker-compose.staging.yml up --build -d

# Visit:
# App: http://localhost:8081/
# Prometheus: http://localhost:9090/
# Grafana: http://localhost:3000/ (admin/admin)
```
