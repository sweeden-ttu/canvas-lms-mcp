"""Pydantic schemas for Bayesian reasoning agents."""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
import uuid


class HypothesisStatus(str, Enum):
    """Status of a hypothesis."""
    PENDING = "pending"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    DESIGNED = "designed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceType(str, Enum):
    """Type of evidence collected."""
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    NEUTRAL = "neutral"


class BayesianBelief(BaseModel):
    """Represents a Bayesian belief with prior and posterior probabilities."""
    
    prior: float = Field(..., ge=0.0, le=1.0, description="Prior probability P(H)")
    likelihood: float = Field(default=0.5, ge=0.0, le=1.0, description="Likelihood P(E|H)")
    likelihood_null: float = Field(default=0.5, ge=0.0, le=1.0, description="P(E|not H)")
    posterior: Optional[float] = Field(None, ge=0.0, le=1.0, description="Posterior P(H|E)")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in estimate")
    
    def update(self, evidence_supports: bool, strength: float = 0.7) -> "BayesianBelief":
        """Update belief based on new evidence using Bayes' theorem.
        
        P(H|E) = P(E|H) * P(H) / P(E)
        where P(E) = P(E|H) * P(H) + P(E|not H) * P(not H)
        """
        if evidence_supports:
            likelihood = strength
            likelihood_null = 1 - strength
        else:
            likelihood = 1 - strength
            likelihood_null = strength
        
        # Calculate marginal probability P(E)
        marginal = likelihood * self.prior + likelihood_null * (1 - self.prior)
        
        # Calculate posterior P(H|E)
        if marginal > 0:
            posterior = (likelihood * self.prior) / marginal
        else:
            posterior = self.prior
        
        return BayesianBelief(
            prior=self.prior,
            likelihood=likelihood,
            likelihood_null=likelihood_null,
            posterior=posterior,
            confidence=min(1.0, self.confidence + 0.1),
        )


class Evidence(BaseModel):
    """Evidence collected from an experiment."""
    
    id: str = Field(default_factory=lambda: f"evi-{uuid.uuid4().hex[:8]}")
    experiment_id: str = Field(..., description="ID of the experiment that produced this evidence")
    type: EvidenceType = Field(..., description="Type of evidence")
    description: str = Field(..., description="Description of the evidence")
    data: dict[str, Any] = Field(default_factory=dict, description="Raw evidence data")
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Strength of evidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def supports_hypothesis(self) -> bool:
        """Check if evidence supports the hypothesis."""
        return self.type == EvidenceType.SUPPORTING


class Experiment(BaseModel):
    """An experiment designed to test a hypothesis."""
    
    id: str = Field(default_factory=lambda: f"exp-{uuid.uuid4().hex[:8]}")
    hypothesis_id: str = Field(..., description="ID of the hypothesis being tested")
    description: str = Field(..., description="Description of the experiment")
    methodology: str = Field(default="", description="Methodology for the experiment")
    expected_outcome: str = Field(..., description="Expected outcome if hypothesis is true")
    success_criteria: str = Field(..., description="Criteria for determining success")
    null_outcome: str = Field(default="", description="Expected outcome if hypothesis is false")
    status: ExperimentStatus = Field(default=ExperimentStatus.DESIGNED)
    results: dict[str, Any] = Field(default_factory=dict, description="Experimental results")
    evidence_ids: list[str] = Field(default_factory=list, description="IDs of collected evidence")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Hypothesis(BaseModel):
    """A testable hypothesis with associated experiments and evidence."""
    
    id: str = Field(default_factory=lambda: f"hyp-{uuid.uuid4().hex[:8]}")
    statement: str = Field(..., description="The hypothesis statement")
    rationale: str = Field(default="", description="Rationale for the hypothesis")
    predictions: list[str] = Field(default_factory=list, description="Predictions if hypothesis is true")
    belief: BayesianBelief = Field(default_factory=lambda: BayesianBelief(prior=0.5))
    status: HypothesisStatus = Field(default=HypothesisStatus.PENDING)
    parent_hypothesis_id: Optional[str] = Field(None, description="Parent hypothesis if refined")
    experiment_ids: list[str] = Field(default_factory=list, description="Associated experiment IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_actionable(self) -> bool:
        """Check if hypothesis is ready for testing."""
        return self.status == HypothesisStatus.PENDING and len(self.predictions) > 0


class WorktreeSchema(BaseModel):
    """Schema for creating a git worktree for hypothesis exploration."""
    
    schema_id: str = Field(default_factory=lambda: f"wts-{uuid.uuid4().hex[:8]}")
    hypothesis: Hypothesis = Field(..., description="The hypothesis to explore")
    branch_name: str = Field(..., description="Git branch name for the worktree")
    worktree_path: Optional[str] = Field(None, description="Path to created worktree")
    experiments: list[Experiment] = Field(default_factory=list)
    evidence_collected: list[Evidence] = Field(default_factory=list)
    status: str = Field(default="pending", description="Schema status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_hypothesis(cls, hypothesis: Hypothesis, base_branch: str = "main") -> "WorktreeSchema":
        """Create a worktree schema from a hypothesis."""
        # Sanitize hypothesis statement for branch name
        safe_name = hypothesis.statement[:30].lower()
        safe_name = "".join(c if c.isalnum() else "-" for c in safe_name)
        safe_name = safe_name.strip("-")
        
        branch_name = f"experiment/{hypothesis.id}-{safe_name}"
        
        return cls(
            hypothesis=hypothesis,
            branch_name=branch_name,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "schema_id": self.schema_id,
            "hypothesis": self.hypothesis.statement,
            "hypothesis_id": self.hypothesis.id,
            "branch_name": self.branch_name,
            "worktree_path": self.worktree_path,
            "prior_probability": self.hypothesis.belief.prior,
            "posterior_probability": self.hypothesis.belief.posterior,
            "experiments": [
                {
                    "id": exp.id,
                    "description": exp.description,
                    "expected_outcome": exp.expected_outcome,
                    "success_criteria": exp.success_criteria,
                    "status": exp.status.value,
                }
                for exp in self.experiments
            ],
            "evidence_collected": [
                {
                    "id": evi.id,
                    "type": evi.type.value,
                    "description": evi.description,
                    "strength": evi.strength,
                }
                for evi in self.evidence_collected
            ],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
