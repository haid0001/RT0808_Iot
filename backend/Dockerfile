FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install fastapi \
    && pip install "uvicorn[standard]" \
    && pip install psycopg2-binary \
    && pip install sqlalchemy \
    && pip install pydantic \
    && pip install paho-mqtt \
    && pip install aiocoap \
    && pip install pytest \
    && pip install httpx




COPY app ./app
COPY test ./test

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
