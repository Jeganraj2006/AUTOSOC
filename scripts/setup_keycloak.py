"""Reconcile local AutoSOC OIDC configuration and development identities.

Secrets are read only from local environment files. Development passwords are
generated at runtime and written only to the protected handoff file outside the
repository; they are never printed or embedded in source.
"""

import os
import secrets
import string
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx as requests


REALM_NAME = "autosoc"
CLIENT_ID = "autosoc-frontend"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HANDOFF_PATH = Path("E:/AUTOSOC/secrets/DEV_LOGIN_CREDENTIALS.txt")


@dataclass(frozen=True)
class DevelopmentAccount:
    username: str
    display_role: str
    realm_role: str


DEVELOPMENT_ACCOUNTS = (
    DevelopmentAccount("autosoc_admin", "Administrator", "administrator"),
    DevelopmentAccount("autosoc_analyst", "Security Analyst", "soc_analyst"),
    DevelopmentAccount("autosoc_viewer", "Read-only Viewer", "viewer"),
)


def load_local_compose_environment() -> None:
    """Load local Compose values when this bootstrap is run from the repository."""
    environment_file = REPOSITORY_ROOT / "infrastructure" / "docker" / ".env"
    if not environment_file.exists():
        return
    for line in environment_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip())


def keycloak_url() -> str:
    return os.getenv("AUTOSOC_KEYCLOAK_URL", "http://127.0.0.1:8080").rstrip("/")


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set before Keycloak bootstrap can run")
    return value


def get_admin_token() -> str:
    response = requests.post(
        f"{keycloak_url()}/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": required_env("AUTOSOC_KEYCLOAK_ADMIN_USER"),
            "password": required_env("AUTOSOC_KEYCLOAK_ADMIN_PASSWORD"),
            "grant_type": "password",
        },
        timeout=10,
    )
    response.raise_for_status()
    return str(response.json()["access_token"])


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def create_realm(token: str) -> None:
    response = requests.post(
        f"{keycloak_url()}/admin/realms",
        headers=headers(token),
        json={
            "realm": REALM_NAME,
            "enabled": True,
            "registrationAllowed": False,
            "loginWithEmailAllowed": True,
            "resetPasswordAllowed": True,
            "verifyEmail": False,
        },
        timeout=10,
    )
    if response.status_code not in (201, 409):
        response.raise_for_status()


def create_or_update_client(token: str) -> None:
    client_payload: dict[str, Any] = {
        "clientId": CLIENT_ID,
        "protocol": "openid-connect",
        "clientAuthenticatorType": "client-secret",
        "secret": required_env("AUTOSOC_KEYCLOAK_FRONTEND_CLIENT_SECRET"),
        "enabled": True,
        "publicClient": False,
        "directAccessGrantsEnabled": False,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "serviceAccountsEnabled": False,
        "redirectUris": ["http://localhost:3000/*", "http://127.0.0.1:3000/*"],
        "webOrigins": ["http://localhost:3000", "http://127.0.0.1:3000"],
    }
    client_url = f"{keycloak_url()}/admin/realms/{REALM_NAME}/clients"
    response = requests.get(client_url, headers=headers(token), params={"clientId": CLIENT_ID}, timeout=10)
    response.raise_for_status()
    existing_clients = response.json()
    if existing_clients:
        response = requests.put(
            f"{client_url}/{existing_clients[0]['id']}",
            headers=headers(token),
            json={**existing_clients[0], **client_payload},
            timeout=10,
        )
    else:
        response = requests.post(client_url, headers=headers(token), json=client_payload, timeout=10)
    response.raise_for_status()


def ensure_realm_role(token: str, name: str) -> dict[str, Any]:
    role_url = f"{keycloak_url()}/admin/realms/{REALM_NAME}/roles"
    response = requests.post(role_url, headers=headers(token), json={"name": name}, timeout=10)
    if response.status_code not in (201, 409):
        response.raise_for_status()
    response = requests.get(f"{role_url}/{name}", headers=headers(token), timeout=10)
    response.raise_for_status()
    return response.json()


def generate_password() -> str:
    # 32 characters from this alphabet have more than 190 bits of entropy.
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))


def create_or_update_development_user(
    token: str, account: DevelopmentAccount, password: str, rotate_passwords: bool
) -> tuple[str, bool]:
    users_url = f"{keycloak_url()}/admin/realms/{REALM_NAME}/users"
    response = requests.get(users_url, headers=headers(token), params={"username": account.username, "exact": "true"}, timeout=10)
    response.raise_for_status()
    users = response.json()
    payload = {
        "username": account.username,
        "enabled": True,
        "emailVerified": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }
    if users:
        user_id = str(users[0]["id"])
        # Reconcile the account and role without silently replacing a working
        # local credential on every repeatable setup invocation.  A deliberate
        # rotation is opt-in and the new password remains outside the repo.
        existing_payload = {**users[0], "enabled": True, "emailVerified": True}
        response = requests.put(
            f"{users_url}/{user_id}",
            headers=headers(token),
            json=existing_payload,
            timeout=10,
        )
        response.raise_for_status()
        if rotate_passwords:
            response = requests.put(
                f"{users_url}/{user_id}/reset-password",
                headers=headers(token),
                json={"type": "password", "value": password, "temporary": False},
                timeout=10,
            )
            response.raise_for_status()
        return user_id, rotate_passwords

    response = requests.post(users_url, headers=headers(token), json=payload, timeout=10)
    response.raise_for_status()
    response = requests.get(users_url, headers=headers(token), params={"username": account.username, "exact": "true"}, timeout=10)
    response.raise_for_status()
    return str(response.json()[0]["id"]), True


def assign_realm_role(token: str, user_id: str, role: dict[str, Any]) -> None:
    response = requests.post(
        f"{keycloak_url()}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm",
        headers=headers(token),
        json=[{"id": role["id"], "name": role["name"]}],
        timeout=10,
    )
    response.raise_for_status()


def credential_handoff_path() -> Path:
    path = Path(os.getenv("AUTOSOC_DEV_CREDENTIALS_PATH", str(DEFAULT_HANDOFF_PATH))).resolve()
    if path.is_relative_to(REPOSITORY_ROOT.resolve()):
        raise RuntimeError("AUTOSOC_DEV_CREDENTIALS_PATH must be outside the repository")
    return path


def write_credential_handoff(credentials: list[tuple[DevelopmentAccount, str]]) -> None:
    path = credential_handoff_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "AutoSOC local development login credentials",
        "",
        "Application login URL: http://127.0.0.1:3000/login",
        f"Keycloak realm: {REALM_NAME}",
        "",
    ]
    for account, password in credentials:
        lines.extend(
            [
                f"Username: {account.username}",
                f"Initial password: {password}",
                f"Assigned role: {account.display_role} ({account.realm_role})",
                "Verified successfully: pending browser authentication",
                "",
            ]
        )
    lines.append("Store locally only. This file is intentionally outside the Git repository.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    try:
        load_local_compose_environment()
        token = get_admin_token()
        create_realm(token)
        create_or_update_client(token)
        rotate_passwords = os.getenv("AUTOSOC_ROTATE_DEV_PASSWORDS", "").lower() in {"1", "true", "yes"}
        credentials: list[tuple[DevelopmentAccount, str]] = []
        for account in DEVELOPMENT_ACCOUNTS:
            password = generate_password()
            user_id, password_changed = create_or_update_development_user(
                token, account, password, rotate_passwords
            )
            assign_realm_role(token, user_id, ensure_realm_role(token, account.realm_role))
            if password_changed:
                credentials.append((account, password))
        if credentials:
            write_credential_handoff(credentials)
    except (requests.HTTPError, RuntimeError, KeyError, IndexError) as exc:
        print(f"Keycloak bootstrap failed: {exc}", file=sys.stderr)
        sys.exit(1)
    print("Keycloak realm, OIDC client, roles, and development identities reconciled.")


if __name__ == "__main__":
    main()
