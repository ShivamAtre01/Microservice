# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --target=/app/deps

# Stage 2: Final lightweight image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/deps /app/deps
COPY . .

ENV PYTHONPATH=/app/deps

EXPOSE 5001

CMD ["python", "app.py"]
