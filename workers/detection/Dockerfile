FROM python:3.12-slim-bookworm
WORKDIR /app
RUN pip install uv
ENV UV_PREVIEW=1
COPY packages /app/packages
COPY apps/api /app/apps/api
WORKDIR /app/workers/detection
COPY workers/detection/pyproject.toml .
COPY workers/detection/src ./src
RUN uv pip install --system -e .
COPY workers/detection/ .
ENV PYTHONPATH=/app/apps/api/src
CMD ["python", "-m", "autosoc_detection.main"]
