# Phase 5 UX audit

Date: 2026-10-26. Scope: existing AutoSOC Next.js routes, components, hooks, and authenticated API contracts. This audit was completed before the Phase 5 source changes.

## Baseline and recovery checkpoint

- Accepted Phase 4 source checkpoint: `E:\AUTOSOC\recovery\autosoc-phase4-accepted-20261026T120000\SOURCE_SNAPSHOT.zip`.
- The archive contains 624 tracked/non-ignored source files. It was extracted into `SOURCE_RESTORE_VERIFICATION` and all manifest entries were present.
- Recovery: copy the archive to a safe location, extract it over a checkout at base commit `32135f71e0f80e73bb95cb4cf16b18d25ee23768`, then restore ignored local configuration from the existing machine. Do not restore `.env*`, Docker volumes, or runtime data from this checkpoint.
- No source was reset, staged, committed, or pushed.

## Route inventory and integration

| Area | Existing route(s) | Real client integration |
| --- | --- | --- |
| Monitoring | `/dashboard`, `/events`, `/events/[eventId]`, `/alerts`, `/alerts/[alertId]`, `/incidents`, `/incidents/[incidentId]` | Dashboard, event, alert, incident, notes, and status hooks. |
| Intelligence | `/detection`, `/predictions`, `/agents` | Anomaly, prediction, and agent-execution hooks. |
| Administration | `/data-sources`, `/rules`, `/system-health`, `/audit`, `/profile` | Data source, system health, authenticated-user and route-specific API calls. |
| Account | `/login`, `/profile`, authenticated shell | Auth.js/Keycloak sign-in, refresh recovery, and secure sign-out. |

## Findings

| Priority | Finding | Impact | Phase 5 response |
| --- | --- | --- |
| High | Global CSS mixes light-mode override selectors, `!important`, hard-coded zinc/indigo values, and decorative glass effects. | Themes can disagree and components are difficult to maintain. | Replace with semantic tokens and shared component foundations. |
| High | Navigation is a flat route list with index-based group headings and no desktop collapse behavior. | Information hierarchy, responsive behavior, and role context are weak. | Build grouped navigation, controlled mobile drawer, active state, and compact sidebar. |
| High | Dashboard, events, alerts, and incident views repeat page-local headers, errors, skeletons, table styles, and status colors. | Inconsistent visual hierarchy and duplicated accessibility work. | Add page header, state, status, and table primitives. |
| High | Login is functional but visually sparse and lacks contextual session-error guidance. | Low trust at the identity boundary. | Redesign without changing the Keycloak/OIDC flow. |
| Medium | Dense log table has fixed visual treatments and no small-screen presentation strategy beyond overflow. | Investigation becomes difficult on mobile/tablet. | Standardize responsive table wrapping and compact metadata layouts. |
| Medium | Semantic state is often communicated through color and pulse alone. | Reduced clarity for color-vision and reduced-motion users. | Pair color with text, icon, and accessible labels; support reduced motion. |
| Medium | Role state is inferred differently in page code and shell navigation. | Risk of confusing unauthorized paths, despite correct server enforcement. | Centralize presentation-only role-aware navigation; retain backend authorization. |
| Medium | AI/ML language appears in dense technical labels. | Users can confuse deterministic processing, heuristics, and LLM output. | Introduce explicit evidence, method, and limitation labels. |
| Low | There are only two frontend unit tests. | Core visual and role-aware flows have limited regression coverage. | Add focused component tests for shared system and role-aware UI as implementation proceeds. |

## Accessibility baseline

- Semantic HTML and Lucide icons are present, but several icon-only buttons lack explicit labels.
- Focus styling is inconsistent (`outline-hidden` is used without a uniform replacement in some controls).
- Loading/error states are generally present but differ page to page.
- Color-only badges and animated pulses require text/icon alternatives and `prefers-reduced-motion` support.
- Dialog primitives exist; their focus behavior will be preserved rather than reimplemented.

## Design direction

The redesign adopts the **Signal ledger** system documented in `DESIGN.md`: calm dark operational surfaces, cyan for navigational/interactive intent, semantic colors only for state, and a strong evidence-before-action hierarchy. It is intentionally not a “hacker terminal” theme and does not manufacture live telemetry.
