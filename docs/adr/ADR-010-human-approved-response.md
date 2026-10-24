# ADR-010: Human Approval for Response Execution

## Status
Accepted

## Context
The AI Agent is capable of recommending response actions (e.g., blocking an IP, disabling a user). Allowing an AI to execute these autonomously carries an unacceptable risk of breaking production systems via false positives (NFR-SEC-001).

## Decision
All state-changing response actions recommended by the system (AI or Rule-based) MUST be staged in a "Pending" state and require explicit human approval via the SOC UI before execution.

## Alternatives Considered
- **Fully Autonomous Containment**: Rejected due to extreme risk of denial-of-service on legitimate infrastructure.
- **Autonomous for Low-Risk Actions**: Rejected for the MVP to maintain a consistent security architecture and simplify the initial implementation.

## Positive Consequences
- Ensures human oversight and accountability for all actions.
- Satisfies strict security and safety requirements.
- Builds trust in the AI system by positioning it as a decision-support tool rather than an autonomous actor.

## Negative Consequences
- Increases the Mean Time to Respond (MTTR) compared to a fully autonomous system.
- Requires SOC Analysts to be available to action critical alerts.

## Security Implications
- The API endpoint that transitions an action from "Pending" to "Approved" must strictly enforce RBAC and generate an immutable audit log identifying the user.

## Revisit Conditions
- In the future, highly trusted, deterministic rule matches (e.g., known malware hash) might be permitted to auto-contain, but AI-driven recommendations will always require human approval.
