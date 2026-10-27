# Infrastructure status

Validated on 2026-10-25 against the local Docker Desktop stack on `E:`.

SeaweedFS 4.50 (`sha256:c2658820e763294a9e9de7b36c81e59b879e3459148351aee4e31a126ca64860`) replaces the unavailable MinIO image. It runs the official `weed mini` S3 service, stores data in `E:/AUTOSOC/docker-data/minio`, enforces credentials (unsigned `GET /` returns `403 AccessDenied`), creates `autosoc-raw-events`, and passed SDK upload/download and post-restart persistence checks.

SeaweedFS was tested through the same MinIO Python SDK used by ingestion at `minio:8333`; this establishes compatibility for AutoSOC's object-archive path, not a blanket compatibility claim for every MinIO administrative API.

The active development OpenSearch service intentionally has its security plugin disabled by the pre-existing Compose configuration. It is not production TLS configuration.
