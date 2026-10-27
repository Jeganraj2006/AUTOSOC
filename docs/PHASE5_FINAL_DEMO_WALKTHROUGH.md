# Phase 5.5 local demonstration walkthrough

1. Open `http://127.0.0.1:3000/login` and select **Sign in with AutoSOC Identity**.
2. Use an existing local development identity from `E:\AUTOSOC\secrets\DEV_LOGIN_CREDENTIALS.txt`; the application redirects through Keycloak and returns to the dashboard.
3. In **Log explorer**, query known event text or source IP and page the server-backed results.
4. Open **Incidents**, select a correlated incident, and inspect its linked alerts, ATT&CK mappings, prediction, and persisted local-Ollama investigation.
5. As an analyst, create a response proposal and request review. As an administrator, approve it and select **Validated Dry Run**.
6. Confirm the response record shows a validated-only result: it never attempts external containment.
7. In **Audit Activity**, confirm the review and execution records; in **Response management**, filter by the incident identifier to see the durable proposal/execution history.
8. Sign out through the account menu.

The fresh acceptance evidence used incident `33690706-9e11-42f7-8ce3-4e13c689d10a`; it is development data only. Its response execution was `succeeded`, `verified`, and `validated_only`.
