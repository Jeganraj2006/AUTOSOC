from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Union, Literal

class RuleCondition(BaseModel):
    """
    Represents a condition block.
    Can be a direct field match (exact/regex) or nested logical operator (AND/OR).
    """
    field: Optional[str] = None
    operator: Optional[Literal["equals", "contains", "startswith", "endswith", "regex", "in", "not_in", "exists", "not_exists"]] = "equals"
    value: Optional[Any] = None
    
    # Logical grouping
    AND: Optional[List['RuleCondition']] = None
    OR: Optional[List['RuleCondition']] = None
    NOT: Optional['RuleCondition'] = None

    @model_validator(mode='before')
    @classmethod
    def check_mutually_exclusive(cls, data: Any) -> Any:
        if isinstance(data, dict):
            has_logical = any(data.get(k) is not None for k in ['AND', 'OR', 'NOT'])
            if has_logical and data.get('field') is not None:
                raise ValueError("Cannot specify 'field' along with logical operators (AND/OR/NOT)")
        return data

class ThresholdConfig(BaseModel):
    count: int = Field(gt=1, description="Number of events to match")
    timeframe: int = Field(gt=0, description="Time window in seconds")
    group_by: List[str] = Field(default_factory=list, description="Fields to group the threshold by (e.g. source_ip, username)")
    suppression_window: int = Field(default=3600, description="Suppress duplicate alerts for this group in seconds")

class RuleModel(BaseModel):
    rule_id: str = Field(description="Unique deterministic identifier for the rule")
    name: str = Field(description="Human readable name")
    description: str = Field(description="Detailed description")
    version: str = Field(default="1.0.0")
    enabled: bool = Field(default=True)
    rule_type: Literal["match", "threshold", "sigma", "statistical", "ioc"] = "match"
    severity: Literal["informational", "low", "medium", "high", "critical"] = "low"
    
    event_categories: List[str] = Field(default_factory=list, description="Categories this rule applies to. Empty means all.")
    
    condition: RuleCondition = Field(description="Detection logic predicate")
    
    threshold: Optional[ThresholdConfig] = None
    
    candidate_mitre_techniques: List[str] = Field(default_factory=list)
    investigation_guidance: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # For Sigma subsets: raw sigma YAML dict may be stored here during conversion
    sigma_raw: Optional[Dict[str, Any]] = None

RuleCondition.model_rebuild()
