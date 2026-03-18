from pydantic import BaseModel, ConfigDict
from enum import Enum

class Verdict(str, Enum):
    VETO = "VETO"
    PAUSE = "PAUSE"
    CLEAR = "CLEAR"

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Flag(BaseModel):
    flag_type: str
    severity: Severity
    evidence: str
    suggestion: str

class PersonaReaction(BaseModel):
    persona_name: str
    emotional_reaction: str  # emoji
    clarity_score: int
    friction_risk: Severity
    narrative: str

class ScoreBreakdown(BaseModel):
    tone: int
    clarity: int
    psych_safety: int
    engagement: int

class AnalysisResult(BaseModel):
    model_config = ConfigDict(strict=False)
    
    social_health_score: int
    score_breakdown: ScoreBreakdown
    persona_reactions: list[PersonaReaction]
    reviewer_verdicts: list[dict]  # Simplified for scaffold
    tone_rewrites: list[dict]
