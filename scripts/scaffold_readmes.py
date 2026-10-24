import os

workers = {
    "ingestion": {"phase": "6", "inputs": "Raw Syslog/API", "outputs": "security.events.raw", "boundary": "Public Ingress"},
    "normalization": {"phase": "7", "inputs": "security.events.raw", "outputs": "security.events.normalized", "boundary": "Internal"},
    "detection": {"phase": "8", "inputs": "security.events.normalized", "outputs": "security.detections", "boundary": "Internal"},
    "correlation": {"phase": "11", "inputs": "security.detections", "outputs": "PostgreSQL Alerts/Incidents", "boundary": "Internal"},
    "prediction": {"phase": "10", "inputs": "PostgreSQL Incidents", "outputs": "Attack Graphs", "boundary": "Internal"},
    "agents": {"phase": "15", "inputs": "security.agent.tasks", "outputs": "PostgreSQL Actions", "boundary": "Restricted execution"}
}

for w, details in workers.items():
    content = f"""# {w.title()} Worker

**Planned Implementation Phase:** Phase {details['phase']}
**Status:** ⚠️ NOT YET IMPLEMENTED ⚠️

## Future Responsibility
This directory will contain the {w} background worker. 

## Interfaces
- **Expected Inputs:** {details['inputs']}
- **Expected Outputs:** {details['outputs']}

## Security Boundary
**{details['boundary']}**: Operates with strict privileges.
"""
    with open(f"workers/{w}/README.md", "w", encoding="utf-8") as f:
        f.write(content)

packages = ["event-schemas", "shared-python", "shared-typescript"]
for p in packages:
    content = f"""# {p}

**Status:** ⚠️ NOT YET IMPLEMENTED ⚠️
This shared package will be implemented in future phases. Do not place application-specific logic here.
"""
    with open(f"packages/{p}/README.md", "w", encoding="utf-8") as f:
        f.write(content)

ml_dirs = ["datasets", "preprocessing", "features", "training", "evaluation", "inference", "notebooks"]
for d in ml_dirs:
    content = f"""# ML {d.title()}

**Status:** ⚠️ NOT YET IMPLEMENTED (Phase 10) ⚠️
This directory is reserved for ML artifacts. Notebooks must not become authoritative implementation sources.
"""
    with open(f"ml/{d}/README.md", "w", encoding="utf-8") as f:
        f.write(content)

infra_dirs = [
    ("rules/sigma", "Phase 8"), ("rules/correlation", "Phase 11"), ("rules/response-playbooks", "Phase 16"),
    ("infrastructure/docker", "Phase 17"), ("infrastructure/kubernetes", "Phase 17"), 
    ("infrastructure/monitoring", "Phase 4"), ("infrastructure/keycloak", "Phase 5")
]
for d, phase in infra_dirs:
    content = f"""# {d.split('/')[-1].title()}

**Status:** ⚠️ NOT YET IMPLEMENTED ({phase}) ⚠️
This directory is reserved for future configuration and rules.
"""
    with open(f"{d}/README.md", "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolding created successfully.")
