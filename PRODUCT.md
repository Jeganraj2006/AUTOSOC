# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Security operations administrators, analysts, and read-only viewers working with live and synthetic security telemetry. Administrators review high-impact response proposals; analysts investigate and propose; viewers inspect evidence and history without mutation access.

## Product Purpose

AutoSOC is a security operations center application that ingests, normalizes, detects, correlates, predicts, and investigates security activity. It helps operators move from event evidence to a reviewable, auditable response recommendation without silently executing destructive containment.

## Positioning

The product combines persisted SOC evidence, deterministic graph processing, local-model-assisted investigation, and server-enforced human approval into one operational workflow.

## Operating Context

Operators work in a time-sensitive monitoring and investigation environment. The application presents events, alerts, incidents, predictions, AI investigation telemetry, response proposals, source health, rules, and audit activity from existing authenticated API endpoints.

## Capabilities and Constraints

- Next.js App Router frontend using Tailwind, Base UI/Radix-compatible components, Lucide, and TanStack Query.
- Keycloak/OIDC authentication and backend JWT/RBAC enforcement are working and must remain authoritative.
- Existing backend data, Docker volumes, credentials, and workers are preserved.
- Real actions are limited to approved `dry_run` validation; the UI must never imply real containment occurred.
- Deterministic investigation stages and model-generated conclusions must remain distinguishable.
- Dark mode is the default; light mode and WCAG 2.2 AA where practicable are required.

## Brand Commitments

AutoSOC is a professional enterprise security operations product. Its visual identity must use a deep navy/graphite operating surface with restrained cyan/blue operational accents and unambiguous semantic states.

## Evidence on Hand

The accepted Phase 4 synthetic pipeline, real backend API contracts, Keycloak-authenticated roles, persisted incidents and investigations, and the existing frontend routes/hooks are available locally. No claims, threat counts, model confidence, or containment effects may be fabricated.

## Product Principles

1. Evidence and current state are legible before action controls.
2. Security-critical actions are explicit, role-aware, and auditable.
3. Operational telemetry is honest about loading, failure, sample data, and uncertainty.
4. Dense information remains scannable across desktop and mobile use.

## Accessibility & Inclusion

Use semantic controls, visible keyboard focus, non-color severity labels, responsive layouts, reduced-motion support, and sufficient contrast. Target WCAG 2.2 AA where practicable.
