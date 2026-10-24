# ADR-017: uv for Python Workspace and Dependencies

## Status
Accepted

## Context
The Python backend (FastAPI), workers, and ML training scripts require a fast, reproducible environment. Standard `pip` and `venv` can be slow, and `Poetry` has historically had slow dependency resolution.

## Decision
We will use `uv` (by Astral) as the primary Python package installer and virtual environment manager.

## Alternatives Considered
- `pip` + `requirements.txt`: Lacks robust locking and workspace features.
- `Poetry`: Slower resolution, heavy overhead.

## Positive Consequences
- Blazing fast installations (Rust-based).
- Integrated `pyproject.toml` support and locking.

## Negative Consequences
- Relatively new tool, though rapidly adopting industry standard formats.

## Security Implications
- Generates reproducible `uv.lock` files, mitigating supply chain attacks via dependency shifting.
