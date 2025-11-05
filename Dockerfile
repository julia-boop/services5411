# ---------- Stage 1: Build ----------
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy project files
COPY app.py .
COPY requirements.txt .
COPY index.html .
COPY styles.css .
COPY script.js .
COPY .env .env

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Flask default)
EXPOSE 8080

# ---------- Stage 2: Run ----------
CMD ["python", "app.py"]
