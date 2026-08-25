FROM python:3.11-slim

WORKDIR /app

# Install system dependencies & Playwright dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
