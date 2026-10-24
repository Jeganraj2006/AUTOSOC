FROM python:3.12-slim-bookworm
WORKDIR /app
RUN pip install uv
ENV UV_PREVIEW=1
COPY packages /app/packages
COPY apps/api /app/apps/api
ENV PYTHONPATH=/app/apps/api/src
WORKDIR /app/workers/correlation
COPY workers/correlation/pyproject.toml .
COPY workers/correlation/src ./src
RUN uv pip install --system -e .
COPY workers/correlation/ .
CMD ["python", "-m", "autosoc_correlation.main"]
