from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ActionableFeedback(BaseModel):
    dimension: str = Field(..., description="The dimension being critiqued (e.g., Groundedness, Recall)")
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    issue_description: str
    actionable_fix: str
    reference_snippets: List[str] = Field(default_factory=list, description="Snippets from the source text that are relevant to the issue")

class QuantitativeScores(BaseModel):
    groundedness: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    logical_consistency: float = Field(..., ge=0.0, le=1.0)
    instruction_following: float = Field(..., ge=0.0, le=1.0)

class IterationMetadata(BaseModel):
    iteration_id: int
    timestamp: str

class CritiqueResult(BaseModel):
    iteration_metadata: IterationMetadata
    global_status: Literal["PASS", "FAIL"]
    quantitative_scores: QuantitativeScores
    actionable_feedback: List[ActionableFeedback]
    critic_confidence_score: float = Field(..., ge=0.0, le=1.0)
