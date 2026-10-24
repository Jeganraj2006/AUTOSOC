FROM python:3.12-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY ml /app/ml
COPY apps/api /app/apps/api
WORKDIR /app/workers/prediction
COPY workers/prediction/requirements.txt .
RUN pip install uv
ENV UV_PREVIEW=1
RUN uv pip install --system -r requirements.txt
COPY workers/prediction/ .
ENV PYTHONPATH=/app/apps/api/src:/app/ml
CMD ["python", "main.py"]
