FROM python:3.10-slim

WORKDIR /app

# System dependencies for compiling some packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

# Gunicorn setup binding to 0.0.0.0:7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "120", "app_ui:app"]
