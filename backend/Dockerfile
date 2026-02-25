FROM python:3.12-slim AS builder

WORKDIR /wheels
RUN pip install --no-cache-dir --upgrade pip wheel

COPY backend/requirements.txt /wheels/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /wheels/requirements.txt

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY backend/ /app/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]