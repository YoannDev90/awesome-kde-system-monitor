FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-gi \
    gir1.2-glib-2.0 \
    libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

CMD ["python", "-m", "generate_pages", "--list-sensors"]
