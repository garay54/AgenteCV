FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY knowledge ./knowledge

USER 10001

EXPOSE 8080

CMD ["sh", "-c", "python -m scripts.ensure_index && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --no-access-log"]