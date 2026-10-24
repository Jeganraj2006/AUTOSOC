# ADR-016: pnpm Workspaces for Frontend and Shared TS

## Status
Accepted

## Context
AutoSOC requires a modern frontend (Next.js) and will eventually require shared TypeScript schemas (e.g., for event definitions) across potential future Node.js utilities.

## Decision
We will use `pnpm` workspaces for the JavaScript/TypeScript ecosystem.

## Alternatives Considered
- `npm` workspaces: Slower, larger footprint on disk.
- `yarn`: Outdated (v1) or overly complex (v2+ Plug'n'Play).

## Positive Consequences
- Very fast installation times due to content-addressable storage.
- Strict dependency hoisting prevents ghost dependencies.

## Negative Consequences
- Slightly less universal than `npm`.

## Security Implications
- Strict linking prevents accidental inclusion of vulnerable transient dependencies that were not explicitly requested.
