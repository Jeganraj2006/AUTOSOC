import jwt
from autosoc_api.core.config import settings
from autosoc_api.core.logging import get_logger
from autosoc_api.auth.models import Principal
from fastapi import HTTPException, status

logger = get_logger(__name__)

class KeycloakJWTValidator:
    def __init__(self):
        self.jwks_url = settings.KEYCLOAK_JWKS_URL
        self.audience = settings.KEYCLOAK_AUDIENCE
        self.issuer = f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}"
        self._jwks_client = jwt.PyJWKClient(self.jwks_url)

    def validate_token(self, token: str) -> Principal:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iat", "sub"]},
                leeway=30,
            )
        except Exception as exc:
            # Authentication must fail closed.  In particular, an unreachable JWKS
            # endpoint is never a reason to trust unverified token claims.
            # Authentication failures can be triggered by attacker-controlled
            # bearer strings.  Log only the exception class so no token-derived
            # content can be copied into application logs.
            logger.warning("Keycloak token validation failed: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles") or payload.get("roles") or []

        return Principal(
            subject_id=str(payload["sub"]),
            username=str(payload.get("preferred_username") or payload["sub"]),
            email=payload.get("email"),
            roles=[str(role) for role in roles] if isinstance(roles, list) else [],
            issuer=str(payload["iss"]),
        )

validator = KeycloakJWTValidator()
