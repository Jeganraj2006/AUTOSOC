from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from autosoc_response.policy.types import ActionType, ExecutionMode, ImpactLevel, ReversibilityType

class PlaybookStep(BaseModel):
    executor: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class ResponsePlaybook(BaseModel):
    playbook_id: str
    name: str
    version: str
    description: str
    action_type: ActionType
    allowed_modes: List[ExecutionMode]
    required_permissions: List[str]
    supported_target_types: List[str]
    impact_level: ImpactLevel
    reversible: ReversibilityType
    approval_required: bool
    timeout: int
    max_scope: int
    preconditions: List[str] = Field(default_factory=list)
    execution_steps: List[PlaybookStep]
    verification_steps: List[PlaybookStep] = Field(default_factory=list)
    rollback_steps: List[PlaybookStep] = Field(default_factory=list)
    evidence_requirements: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # We explicitly forbid certain shell properties in validation, but these attributes don't exist here.
    # The Pydantic model naturally drops or rejects unknown fields if we set strict=True.
    model_config = {"extra": "forbid"}
