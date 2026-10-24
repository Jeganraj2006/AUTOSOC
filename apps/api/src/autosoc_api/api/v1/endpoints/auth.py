from fastapi import APIRouter, Depends
from autosoc_api.auth.models import Principal
from autosoc_api.auth.dependencies import get_current_principal, require_permission
from autosoc_api.auth.permissions import Permissions

router = APIRouter()

@router.get("/me", response_model=Principal)
async def get_current_user_context(
    principal: Principal = Depends(get_current_principal)
):
    """
    Returns the authenticated user's context including parsed roles and permissions.
    """
    return principal

@router.get("/test-admin")
async def get_admin_only_data(
    principal: Principal = Depends(require_permission(Permissions.USERS_MANAGE))
):
    """
    Test endpoint enforcing administrator access.
    """
    return {"status": "success", "message": "Admin access granted."}
