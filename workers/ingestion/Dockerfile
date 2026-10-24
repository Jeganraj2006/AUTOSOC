FROM python:3.12-slim-bookworm
WORKDIR /app
RUN pip install uv
ENV UV_PREVIEW=1
COPY packages /app/packages
COPY apps/api /app/apps/api
WORKDIR /app/workers/ingestion
COPY workers/ingestion/pyproject.toml .
COPY workers/ingestion/src ./src
RUN uv pip install --system -e .
COPY workers/ingestion/ .
ENV PYTHONPATH=/app/apps/api/src
EXPOSE 8000
EXPOSE 5140/udp
CMD ["uvicorn", "autosoc_ingestion.main:app", "--host", "0.0.0.0", "--port", "8000"]
