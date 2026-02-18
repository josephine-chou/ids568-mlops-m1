# Builder stage
FROM python:3.11-slim as builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY app/ .

ENV PATH=/root/.local/bin:$PATH
ENV PORT=8080
EXPOSE 8080

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}