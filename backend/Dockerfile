FROM python:3.11-slim

WORKDIR /app

# Prevent Python buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Increase pip timeout
ENV PIP_DEFAULT_TIMEOUT=1000

# Install system dependencies
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements first
COPY requirements.txt .

# Install dependencies with retries
RUN pip install --no-cache-dir --retries 10 -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]