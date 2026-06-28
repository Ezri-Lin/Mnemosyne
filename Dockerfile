FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y \
    calibre \
    poppler-utils \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.server:app"]
