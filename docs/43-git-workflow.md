# Git Workflow

We follow a structured branching model:

## Branches
- `main`: Production-ready code. Protected branch.
- `develop`: Integration branch. Default target for features.
- `feature/*`: New functionality.
- `fix/*`: Bug fixes.
- `docs/*`: Documentation updates.
- `experiment/*`: ML experiments (do not merge to main).

## Pull Requests
- Must pass all CI checks (Frontend CI, Backend CI, Security).
- Must include updated tests.
- Rebase and resolve conflicts locally before requesting review.

## Commit Messages
Use Conventional Commits syntax:
- `feat: [description]`
- `fix: [description]`
- `chore: [description]`
- `docs: [description]`
