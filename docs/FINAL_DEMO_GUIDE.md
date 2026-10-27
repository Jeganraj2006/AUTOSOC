# Final demonstration guide

1. Confirm `docker compose -f infrastructure/docker/compose.yml ps` lists all 12 services and API/UI health endpoints respond.
2. Sign in at `http://127.0.0.1:3000/login` using the protected development handoff file.
3. Show dashboard totals, then Events filtering/search and the corresponding Alert.
4. Open the correlated Incident and show its alert/event evidence and ATT&CK mappings.
5. Show persisted prediction and the completed local-Ollama investigation; explain that it is advisory, local, and evidence-grounded.
6. As analyst, create a response proposal and request approval. As administrator, approve it and execute only `dry_run`.
7. Show the resulting execution record and audit event. State that `validated_only` means no external containment was attempted.
8. Sign in as viewer and show read-only navigation; mutation requests are denied. Logout.

Use only synthetic data in a demonstration. Do not screen-share credentials, bearer tokens, API keys, Keycloak admin pages, Compose `.env`, or the protected credentials handoff file.
