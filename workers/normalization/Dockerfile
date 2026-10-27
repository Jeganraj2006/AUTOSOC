FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir uv==0.2.11
ENV UV_SYSTEM_PYTHON=1
ENV UV_PREVIEW=1
WORKDIR /app
COPY packages /app/packages
COPY apps/api /app/apps/api
WORKDIR /app/workers/normalization
COPY workers/normalization/pyproject.toml workers/normalization/README.md ./
COPY workers/normalization/src ./src
RUN uv pip install --system -e .
ENV PYTHONPATH=/app/apps/api/src
CMD ["python", "-m", "autosoc_normalization.main"]
