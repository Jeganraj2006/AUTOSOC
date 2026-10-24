<rule>
name: autosoc-phase-boundary
description: Enforces strict adherence to the current project phase.

instructions: |
  1. ALWAYS check the current project phase in `README.md`.
  2. NEVER implement functionality belonging to future phases. If a user asks you to implement a database model in Phase 3, politely decline and explain that databases are configured in Phase 4.
  3. ALWAYS preserve existing requirement identifiers (e.g., FR-AUTH-001) and architectural decisions (ADR-001). Do not silently rename them.
</rule>
