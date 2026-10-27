# Phase 5 design system

## Signal ledger

AutoSOC’s operating UI uses semantic CSS tokens, not route-specific theme overrides. Dark mode is the default graphite/navy control room; light mode is a complete neutral operational counterpart. Cyan identifies navigation, focus, and primary user intent. Green, amber, red, and violet are reserved for meaningfully different states.

## Foundations implemented

- Global semantic color, surface, border, focus, and typography tokens in `apps/web/src/app/globals.css`.
- Default dark and persisted light-theme behavior in the application shell.
- Visible focus, selection, scrollbar, tabular-number, and reduced-motion foundations.
- Shared `PageHeader` and `OperationalState` primitives.
- Refined shared severity/status indicators: label and icon accompany color.
- Shared surface/KPI styling applied to the dashboard metrics.

## Navigation

The shell groups routes into Monitoring, Intelligence, and Administration; supports active route context, an accessible compact desktop sidebar, responsive mobile drawer, authenticated account menu, secure sign-out, API health state, and theme control. Audit Activity remains presentation-gated to administrators; backend RBAC remains authoritative.

## Compatibility

A constrained light-theme compatibility bridge keeps established zinc-based route classes legible while routes are migrated to semantic tokens. It is transitional, not a replacement for route-level modernization.
