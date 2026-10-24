from pydantic import BaseModel
from typing import List, Optional

class Principal(BaseModel):
    """
    Typed authenticated principal model representing the current user or service account.
    """
    subject_id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    issuer: str
