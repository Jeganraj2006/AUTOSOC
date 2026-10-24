# Agent Security Architecture

The Agentic AI subsystem (powered by LangGraph and Ollama) operates under strict security constraints to prevent autonomous destructive actions and data leakage.

## Strict Agent Restrictions (Phase 1 Mandates)
- **NO unrestricted shell commands**: The agent does not have a `subprocess` or `bash` tool.
- **NO direct production credential access**: The agent cannot read Vault, `.env` files, or Keycloak admin credentials.
- **NO independent destructive actions**: The agent CANNOT execute response playbooks. It can only propose them.
- **NO unvalidated trust**: Retrieved RAG content is treated as untrusted string literals, not instructions.
- **NO authorization bypass**: The agent cannot override RBAC checks.
- **Advisory Output**: All LLM output is marked as advisory and must be validated by a human analyst.

## Agent Roles and Permissions

The Agent operates under a dedicated Service Account with a highly restricted permission matrix:

| Resource | Permission | Purpose |
| :--- | :--- | :--- |
| **OpenSearch (Logs)** | Read-Only | RAG queries for context gathering. |
| **PostgreSQL (Alerts)** | Read-Only | Reading alert metadata. |
| **PostgreSQL (Agent Tasks)**| Read/Write | Updating task status (In Progress, Complete). |
| **PostgreSQL (Incidents)** | Update (Specific Fields)| Appending summaries and recommendations. |
| **Redpanda** | None | Agent does not interact directly with streams. |

## Tool Management

### Permitted Tools (Read-Only)
- `search_logs(query: str, time_range: str)`: Executes a scoped query against OpenSearch.
- `get_threat_intel(ip_hash: str)`: Queries external (mock) threat feeds.
- `get_playbooks(incident_type: str)`: Retrieves available response playbooks from the allowlist.

### Prohibited Tools
- `execute_playbook()`: **BLOCKED**. Execution is handled exclusively by the Response API upon human approval.
- `execute_shell()`: **BLOCKED**.
- `update_rule()`: **BLOCKED**.

## Execution Constraints
- **Maximum Execution Steps**: LangGraph `recursion_limit` is strictly set to 5. If the agent does not reach a conclusion, it fails gracefully.
- **Execution Timeouts**: A hard timeout of 60 seconds per task.
- **Kill Switch**: Analysts can terminate a running agent task via the UI.

## Validation and Integrity
- **Input Validation**: All logs passed to the prompt are wrapped in delimiters (e.g., `<<<LOG_START>>> ... <<<LOG_END>>>`) to mitigate prompt injection.
- **Sensitive-Data Masking**: IPs and Usernames are replaced with consistent hashes before LLM ingestion if PII masking is enabled.
- **Output Validation**: Recommended actions are string-matched against the database's Playbook Allowlist. If the LLM hallucinates an action, it is dropped.
- **Citation Requirements**: The system prompt forces the LLM to output `[LogID: 123]` for every factual claim.
- **Audit Trail**: Every LangGraph state transition (tool call, LLM thought process) is saved to the `agent_tasks` table for explainability.
