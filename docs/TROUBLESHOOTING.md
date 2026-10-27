# Troubleshooting

| Symptom | Check | Safe action |
| --- | --- | --- |
| Missing environment file | `Test-Path infrastructure/docker/.env` | Run `pwsh scripts/initialize-local-env.ps1`; never commit the result. |
| Image pull failure | `docker compose -f infrastructure/docker/compose.yml pull` | Check Docker Desktop sign-in, DNS/proxy, disk space, and trusted registry availability. Do not disable TLS. |
| Keycloak login fails | `Invoke-WebRequest http://127.0.0.1:8080/realms/autosoc` | Run `pwsh scripts/setup-dev.ps1`; it preserves existing passwords unless explicit rotation is set. |
| API is not ready | `Invoke-WebRequest http://127.0.0.1:8000/api/v1/health/ready` | Check `E:\AUTOSOC\runtime-logs\local-app` and `docker compose ... ps`. |
| Worker issue | `docker compose -f infrastructure/docker/compose.yml logs --tail 100 <service>` | Restart only the named worker; do not remove volumes. |
| Ollama inference timeout | `ollama list` and `curl http://127.0.0.1:11434/api/tags` | Warm the configured local model; durable retries are bounded. |
| Storage error | `docker compose ... ps minio` | Verify SeaweedFS is healthy and `AUTOSOC_MINIO_DATA_DIR` remains on E: or D:. |

For a controlled shutdown use `pwsh scripts/stop-local.ps1`; it stops containers but preserves Docker volumes and E: storage. Back up PostgreSQL and raw-object storage before upgrades. Do not remove volumes to troubleshoot.
