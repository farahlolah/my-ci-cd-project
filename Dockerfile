FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and tests
COPY src/ src/
COPY tests/ tests/

# Optional: create reports folder inside container
RUN mkdir -p /app/reports

EXPOSE 8080

CMD ["python", "-u", "src/app.py"]
