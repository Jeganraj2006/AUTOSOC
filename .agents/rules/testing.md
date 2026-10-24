<rule>
name: autosoc-testing
description: Enforces testing requirements.

instructions: |
  1. Add tests for every new feature or endpoint.
  2. Run `uv run pytest --cov=src` to verify backend coverage. Do NOT claim tests pass unless you have successfully executed them.
  3. Tests must not require external internet access or production services.
</rule>
