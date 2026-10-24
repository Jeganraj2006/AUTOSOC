# Coding Standards

## Python Style (Backend)
- Standard: PEP 8 (Enforced strictly by Ruff).
- Formatting: Ruff formatter (Black-compatible). Line length 100.
- Typing: Strict typing required. Checked by `mypy`.
- Imports: Grouped and sorted automatically by Ruff (`I` ruleset).

## TypeScript / React Style (Frontend)
- Standard: ESLint (Next.js Core Web Vitals) + Prettier.
- Components: Use shadcn/ui patterns.
- Styling: Tailwind CSS utility classes. Avoid custom CSS unless absolutely necessary.
- State: Favor server components. Use `useState` only for interactive client elements.

## Error Handling
- Never return stack traces to clients.
- Use the standard `ApiError` class in the frontend and `JSONResponse` in the backend.

## Security
- Do not commit secrets. Gitleaks will catch known patterns, but developers must remain vigilant.
- Avoid wildcard `*` for CORS.
