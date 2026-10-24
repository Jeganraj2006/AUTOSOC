<rule>
name: autosoc-python
description: Python specific constraints for AutoSOC.

instructions: |
  1. Use FastAPI and Pydantic v2 conventions.
  2. Enforce strict typing with `mypy`. All public functions must have type hints.
  3. Never use raw `subprocess` execution without explicit architectural review.
</rule>
