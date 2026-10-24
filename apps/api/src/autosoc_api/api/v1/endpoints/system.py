"""System maintenance API. Destructive bulk purge is intentionally disabled.

Historical versions exposed an unauthenticated route that deleted operational
security evidence. Do not re-enable without a separately reviewed, audited,
admin-only maintenance workflow and backup/restore guarantees.
"""
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.delete("/purge-all", deprecated=True)
@router.post("/purge-all", deprecated=True)
async def purge_all_database_records():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Bulk security-evidence deletion is disabled for safety.",
    )
