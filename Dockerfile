FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py .
COPY requirements.txt .
COPY index.html .
COPY styles.css .
COPY script.js .
COPY Logo.png .
COPY Logo2.png .
COPY HeadLogo.png .

RUN pip install --no-cache-dir -r requirements.txt gunicorn

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]