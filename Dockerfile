FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy both source code and tests
COPY src/ src/
COPY tests/ tests/

EXPOSE 8080

CMD ["python", "-u", "src/app.py"]
