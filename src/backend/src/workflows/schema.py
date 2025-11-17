"""Schema para validação de estado."""
from pydantic import BaseModel, Field
from typing import List, Optional


class ParsedQuestion(BaseModel):
    """Pergunta parseada e normalizada."""
    qid: str
    category: str
    question_text: str
    requirements: List[str]
    expected_format: str
    similar_questions: List[str] = Field(default_factory=list)


class GeneratedResponse(BaseModel):
    """Resposta gerada."""
    qid: str
    response_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: List[str] = Field(default_factory=list)
    requires_human_input: bool = False
    human_input_fields: List[str] = Field(default_factory=list)


class VerifiedResponse(BaseModel):
    """Resposta verificada."""
    qid: str
    response_text: str
    confidence_score: float
    is_consistent: bool
    has_prohibited_terms: bool
    has_gaps: bool
    validation_errors: List[str] = Field(default_factory=list)
    needs_review: bool

