import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from autosoc_api.auth.models import Principal
from autosoc_api.auth.keycloak import validator
from autosoc_api.auth.permissions import get_permissions_for_roles
from autosoc_api.core.config import settings

# This schema will be used in OpenAPI for Bearer token documentation
oauth2_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

def get_current_principal(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> Principal:
    """
    Dependency that validates the Bearer token and returns the current Principal.
    Rejects missing or invalid tokens with HTTP 401.
    """
    if not token:
        # In a test environment we might bypass this if explicitly configured, 
        # but for Phase 5 we strictly enforce it unless using dependency overrides in pytest.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    principal = validator.validate_token(token.credentials)
    principal.permissions = get_permissions_for_roles(principal.roles)
    return principal

def require_permission(required_permission: str):
    """
    Dependency generator that checks if the Principal has the required permission.
    Returns HTTP 403 if unauthorized.
    """
    def permission_checker(principal: Principal = Depends(get_current_principal)) -> Principal:
        if required_permission not in principal.permissions:
            logger.warning(
                "authorization denied: username=%s required_permission=%s roles=%s",
                principal.username,
                required_permission,
                ",".join(principal.roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return principal
    return permission_checker

def require_roles(allowed_roles: list[str]):
    """
    Dependency generator that checks if the Principal has at least one of the allowed roles.
    Returns HTTP 403 if unauthorized.
    """
    def role_checker(principal: Principal = Depends(get_current_principal)) -> Principal:
        if not set(allowed_roles).intersection(set(principal.roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough roles"
            )
        return principal
    return role_checker
