# AutoSOC: Agentic AI-Driven Autonomous Security Operations Center

Welcome to the **AutoSOC** project! This is an academic research platform designed to demonstrate the integration of traditional SIEM/SOAR capabilities with cutting-edge Machine Learning and Agentic AI for zero-day threat detection and attack progression prediction.

## Overview
AutoSOC ingests security events, normalizes them, and correlates them into actionable incidents. It utilizes a Hybrid ML approach to identify anomalous behaviors (potential zero-days) and leverages sequence models (LSTMs/Transformers) to predict the next steps in an attacker's campaign according to the MITRE ATT&CK framework.

## Key Features
- **Event Ingestion & Normalization**: Collects and normalizes logs from disparate sources.
- **Hybrid Threat Detection**: Combines deterministic Sigma rules with ML-based anomaly detection.
- **Attack Progression Prediction**: Predicts TTPs to stay one step ahead of attackers.
- **Agentic AI Investigations**: Uses LangGraph and RAG for automated context gathering.
- **Human-in-the-Loop Response**: Enforces strict RBAC and human approval before executing containment playbooks.

## Getting Started
This is a **local-development and academic demonstration release**, not a production-ready security product. See [the deployment guide](docs/DEPLOYMENT_GUIDE.md), [architecture](docs/SYSTEM_ARCHITECTURE.md), [security architecture](docs/SECURITY_ARCHITECTURE.md), [known limitations](docs/KNOWN_LIMITATIONS.md), and [final demo guide](docs/FINAL_DEMO_GUIDE.md).

First generate local-only configuration (it creates only placeholder values and never prints secrets), then initialize infrastructure:
```bash
pwsh scripts/initialize-local-env.ps1
pwsh scripts/setup-dev.ps1
pwsh scripts/start-local.ps1
```

The setup is repeatable: it preserves initialized volumes and existing Keycloak passwords. Explicit credential rotation is opt-in through `AUTOSOC_ROTATE_DEV_PASSWORDS=true`; credentials remain outside this repository.

## Academic Constraints
This project adheres to strict academic constraints. It does not fabricate enterprise SLAs, keeps all agent execution read-only without human approval, and clearly distinguishes between anomalous behaviors and confirmed vulnerabilities.
