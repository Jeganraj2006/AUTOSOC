FROM python:3.12-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install uv
ENV UV_PREVIEW=1
COPY packages /app/packages
COPY apps/api /app/apps/api
WORKDIR /app/workers/agents
COPY workers/agents/pyproject.toml ./
COPY workers/agents/src/ ./src/
RUN uv pip install --system -e .
ENV ENVIRONMENT=development
ENV PYTHONPATH=/app/workers/agents/src:/app/apps/api/src
CMD ["python", "-m", "autosoc_agents.main"]
