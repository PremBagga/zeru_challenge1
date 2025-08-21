# -------------------------------
# 1. Use official Python base image
# -------------------------------
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# -------------------------------
# 2. Install system dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 3. Copy dependencies first (for caching)
# -------------------------------
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# 4. Copy application code
# -------------------------------
COPY . .

# -------------------------------
# 5. Expose FastAPI port
# -------------------------------
EXPOSE 8000

# -------------------------------
# 6. Run app with Uvicorn
# -------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
