# ADR-003: Next.js for Frontend

## Status
Accepted

## Context
AutoSOC requires a highly interactive, responsive, and dynamic web interface for SOC Analysts to monitor alerts, view complex attack graphs (Cytoscape.js), and interact with Agentic AI outputs in real-time.

## Decision
We will use Next.js (React) with TypeScript as the frontend framework.

## Alternatives Considered
- **Vanilla React (Vite/Create React App)**: Rejected because Next.js provides built-in routing, API routes for frontend-specific BFF (Backend-for-Frontend) patterns, and better performance optimizations.
- **Vue.js / Nuxt**: Rejected in favor of the larger React ecosystem, specifically regarding integrations with Cytoscape.js, ECharts, and shadcn/ui.
- **Server-Side Rendered Python (Jinja2)**: Rejected because building highly interactive graph visualizations and real-time streaming interfaces is exceedingly difficult with traditional SSR.

## Positive Consequences
- Component-driven architecture using shadcn/ui and Tailwind CSS ensures a consistent and premium design.
- TypeScript enforces type safety, reducing runtime errors.
- TanStack Query simplifies server-state management and caching on the client.

## Negative Consequences
- Requires a separate Node.js deployment alongside the Python backend.

## Security Implications
- Next.js must securely handle OIDC tokens (e.g., using NextAuth or direct Keycloak integration) and prevent XSS when rendering AI-generated summaries or raw logs.

## Revisit Conditions
- N/A; Next.js is firmly established as the frontend technology for this project.
