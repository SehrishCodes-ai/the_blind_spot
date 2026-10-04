FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files to disc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV HOST=0.0.0.0

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY run.py .

EXPOSE 8080

CMD ["python", "run.py"]
