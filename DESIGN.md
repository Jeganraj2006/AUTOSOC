# AutoSOC design system

## Visual world

**Signal ledger.** AutoSOC is an operational control room, not a cinematic hacker interface: quiet graphite surfaces hold dense evidence, while cyan marks navigation and verified system connection. Semantic color is reserved for risk and outcome, so the interface remains calm when the telemetry is not.

## Mode

Operate. Every surface prioritizes scanning, evidence, state clarity, and safely completing a real SOC task.

## Tokens

- Default theme: deep navy canvas and graphite panels; light theme is an equally complete neutral-paper operational mode.
- Accent: cyan/blue for navigation, focus, and controllable primary actions.
- Semantic states: emerald/healthy, amber/warning, red/critical, violet/AI-assisted.
- Typography: Inter for interface reading; tabular numerals and monospace only for hashes, identifiers, and measurements.
- Shape: restrained 10–14px radii, 1px low-contrast borders, and measured layered shadows. No decorative glass panels or colored card rails.

## Layout

- A collapsible grouped sidebar owns product navigation; the top bar owns context, health, theme, and account controls.
- Every route starts with one page heading and a concise factual description, then exposes actions nearest to the data they affect.
- Tables retain keyboard and horizontal-scroll access on compact screens; mobile replaces desktop navigation with a focused drawer.

## Interaction

- Hover and focus clarify available controls without moving essential content.
- Loading, empty, error, permission, and disabled states use the same shared patterns.
- Animation is limited to status transition feedback and respects reduced-motion preferences.
- Dry-run results are labelled `Validated only`; deterministic graph stages and LLM conclusions are separately labelled.
