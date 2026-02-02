"""
Evidence Evaluator Agent (Agent 2)

Responsibilities:
- Evaluate experimental evidence
- Update beliefs using Bayes' theorem
- Form new/refined hypotheses based on evidence
- Verify results against predictions
- Create git worktrees from schemas
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .schemas import (
    Hypothesis,
    Experiment,
    Evidence,
    WorktreeSchema,
    BayesianBelief,
    HypothesisStatus,
    ExperimentStatus,
    EvidenceType,
)


@dataclass
class EvaluatorConfig:
    """Configuration for the Evidence Evaluator Agent."""
    support_threshold: float = 0.7  # Posterior above this = supported
    refute_threshold: float = 0.3   # Posterior below this = refuted
    strong_evidence_threshold: float = 0.8
    weak_evidence_threshold: float = 0.3
    worktree_base_dir: Path = field(default_factory=lambda: Path("worktrees"))
    schema_dir: Path = field(default_factory=lambda: Path("worktree_schemas"))
    git_repo_path: Path = field(default_factory=lambda: Path("."))


class EvidenceEvaluatorAgent:
    """
    Agent 2: Evaluates evidence, updates beliefs, and creates worktrees.
    
    This agent uses Bayesian reasoning to:
    1. Evaluate experimental evidence
    2. Update hypothesis probabilities using Bayes' theorem
    3. Form refined hypotheses based on evidence
    4. Verify experimental results
    5. Create git worktrees from schemas for parallel exploration
    """
    
    def __init__(self, config: Optional[EvaluatorConfig] = None):
        self.config = config or EvaluatorConfig()
        self.evidence: dict[str, Evidence] = {}
        self.evaluation_history: list[dict] = []
        self.worktrees_created: dict[str, str] = {}  # schema_id -> worktree_path
        
        # Ensure directories exist
        self.config.worktree_base_dir.mkdir(parents=True, exist_ok=True)
    
    def evaluate_evidence(
        self,
        experiment: Experiment,
        observation: str,
        matches_prediction: bool,
        strength: float = 0.7,
        data: Optional[dict] = None,
    ) -> Evidence:
        """
        Evaluate evidence from an experiment.
        
        Args:
            experiment: The experiment that produced the evidence
            observation: Description of what was observed
            matches_prediction: Whether observation matches expected outcome
            strength: Strength of the evidence (0-1)
            data: Raw evidence data
        
        Returns:
            Evidence object with evaluation
        """
        # Determine evidence type
        if strength < self.config.weak_evidence_threshold:
            evidence_type = EvidenceType.NEUTRAL
        elif matches_prediction:
            evidence_type = EvidenceType.SUPPORTING
        else:
            evidence_type = EvidenceType.CONTRADICTING
        
        # Create evidence
        evidence = Evidence(
            experiment_id=experiment.id,
            type=evidence_type,
            description=observation,
            data=data or {},
            strength=strength,
        )
        
        # Store evidence
        self.evidence[evidence.id] = evidence
        
        # Update experiment
        experiment.evidence_ids.append(evidence.id)
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()
        experiment.results = {
            "observation": observation,
            "matches_prediction": matches_prediction,
            "evidence_id": evidence.id,
        }
        
        return evidence
    
    def update_belief(
        self,
        hypothesis: Hypothesis,
        evidence: Evidence,
    ) -> BayesianBelief:
        """
        Update hypothesis belief based on new evidence using Bayes' theorem.
        
        P(H|E) = P(E|H) * P(H) / P(E)
        
        Args:
            hypothesis: The hypothesis to update
            evidence: New evidence to incorporate
        
        Returns:
            Updated BayesianBelief with posterior probability
        """
        # Get current belief (use posterior if available, else prior)
        current_belief = hypothesis.belief
        current_prob = current_belief.posterior or current_belief.prior
        
        # Update belief
        updated_belief = BayesianBelief(prior=current_prob).update(
            evidence_supports=evidence.supports_hypothesis(),
            strength=evidence.strength,
        )
        
        # Store in hypothesis
        hypothesis.belief = updated_belief
        hypothesis.updated_at = datetime.utcnow()
        
        # Update hypothesis status based on posterior
        self._update_hypothesis_status(hypothesis)
        
        # Record in history
        self.evaluation_history.append({
            "hypothesis_id": hypothesis.id,
            "evidence_id": evidence.id,
            "prior": current_prob,
            "posterior": updated_belief.posterior,
            "evidence_type": evidence.type.value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return updated_belief
    
    def _update_hypothesis_status(self, hypothesis: Hypothesis) -> None:
        """Update hypothesis status based on posterior probability."""
        posterior = hypothesis.belief.posterior
        
        if posterior is None:
            return
        
        if posterior >= self.config.support_threshold:
            hypothesis.status = HypothesisStatus.SUPPORTED
        elif posterior <= self.config.refute_threshold:
            hypothesis.status = HypothesisStatus.REFUTED
        else:
            hypothesis.status = HypothesisStatus.INCONCLUSIVE
    
    def form_refined_hypothesis(
        self,
        original: Hypothesis,
        evidence: Evidence,
        refinement: str,
    ) -> Hypothesis:
        """
        Form a refined hypothesis based on evidence.
        
        When evidence doesn't clearly support or refute a hypothesis,
        we may need to refine it.
        
        Args:
            original: The original hypothesis
            evidence: Evidence that prompted refinement
            refinement: The refined hypothesis statement
        
        Returns:
            New refined Hypothesis linked to original
        """
        # Use posterior as prior for refined hypothesis
        prior = original.belief.posterior or original.belief.prior
        
        refined = Hypothesis(
            statement=refinement,
            rationale=f"Refined from {original.id} based on evidence {evidence.id}",
            predictions=original.predictions.copy(),
            belief=BayesianBelief(prior=prior),
            parent_hypothesis_id=original.id,
        )
        
        return refined
    
    def verify_results(
        self,
        experiment: Experiment,
        actual_outcome: str,
    ) -> dict:
        """
        Verify experimental results against predictions.
        
        Args:
            experiment: The experiment to verify
            actual_outcome: What actually happened
        
        Returns:
            Verification result with analysis
        """
        # Compare with expected outcome
        expected = experiment.expected_outcome
        null_expected = experiment.null_outcome
        
        # Simple similarity check (in practice, use more sophisticated comparison)
        matches_expected = self._outcomes_match(actual_outcome, expected)
        matches_null = self._outcomes_match(actual_outcome, null_expected)
        
        verification = {
            "experiment_id": experiment.id,
            "expected_outcome": expected,
            "actual_outcome": actual_outcome,
            "matches_expected": matches_expected,
            "matches_null": matches_null,
            "success_criteria": experiment.success_criteria,
            "verdict": self._determine_verdict(matches_expected, matches_null),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return verification
    
    def _outcomes_match(self, actual: str, expected: str) -> bool:
        """Check if actual outcome matches expected (simple implementation)."""
        # In practice, use NLP or structured comparison
        actual_lower = actual.lower()
        expected_lower = expected.lower()
        
        # Check for key terms
        expected_terms = set(expected_lower.split())
        actual_terms = set(actual_lower.split())
        
        overlap = len(expected_terms & actual_terms)
        total = len(expected_terms)
        
        return (overlap / total) > 0.5 if total > 0 else False
    
    def _determine_verdict(self, matches_expected: bool, matches_null: bool) -> str:
        """Determine verification verdict."""
        if matches_expected and not matches_null:
            return "CONFIRMED"
        elif matches_null and not matches_expected:
            return "REFUTED"
        elif matches_expected and matches_null:
            return "AMBIGUOUS"
        else:
            return "INCONCLUSIVE"
    
    def create_worktree_from_schema(
        self,
        schema: WorktreeSchema,
        start_point: str = "HEAD",
    ) -> Path:
        """
        Create a git worktree from a worktree schema.
        
        Args:
            schema: The worktree schema to use
            start_point: Git ref to start from (default: HEAD)
        
        Returns:
            Path to the created worktree
        """
        worktree_path = self.config.worktree_base_dir / schema.schema_id
        branch_name = schema.branch_name
        
        try:
            # Create the branch if it doesn't exist
            self._run_git_command([
                "branch", branch_name, start_point
            ], check=False)  # Ignore if exists
            
            # Create the worktree
            self._run_git_command([
                "worktree", "add",
                str(worktree_path),
                branch_name,
            ])
            
            # Update schema
            schema.worktree_path = str(worktree_path)
            schema.status = "created"
            
            # Record
            self.worktrees_created[schema.schema_id] = str(worktree_path)
            
            # Save experiment info to worktree
            self._save_experiment_info(worktree_path, schema)
            
            return worktree_path
            
        except subprocess.CalledProcessError as e:
            schema.status = "failed"
            raise RuntimeError(f"Failed to create worktree: {e}")
    
    def _run_git_command(
        self,
        args: list[str],
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git", "-C", str(self.config.git_repo_path)] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
        )
    
    def _save_experiment_info(
        self,
        worktree_path: Path,
        schema: WorktreeSchema,
    ) -> None:
        """Save experiment information to the worktree."""
        info_dir = worktree_path / ".hypothesis"
        info_dir.mkdir(exist_ok=True)
        
        # Save hypothesis info
        with open(info_dir / "hypothesis.json", "w") as f:
            json.dump({
                "id": schema.hypothesis.id,
                "statement": schema.hypothesis.statement,
                "prior": schema.hypothesis.belief.prior,
                "predictions": schema.hypothesis.predictions,
            }, f, indent=2)
        
        # Save experiments
        with open(info_dir / "experiments.json", "w") as f:
            json.dump([
                {
                    "id": exp.id,
                    "description": exp.description,
                    "expected_outcome": exp.expected_outcome,
                    "success_criteria": exp.success_criteria,
                }
                for exp in schema.experiments
            ], f, indent=2)
        
        # Create README for the worktree
        readme_content = f"""# Hypothesis Exploration: {schema.hypothesis.id}

## Hypothesis
{schema.hypothesis.statement}

## Prior Probability
{schema.hypothesis.belief.prior:.2%}

## Experiments to Run

"""
        for exp in schema.experiments:
            readme_content += f"""### {exp.id}
- **Description**: {exp.description}
- **Expected Outcome**: {exp.expected_outcome}
- **Success Criteria**: {exp.success_criteria}

"""
        
        with open(worktree_path / "HYPOTHESIS.md", "w") as f:
            f.write(readme_content)
    
    def create_worktrees_from_schemas_dir(self) -> list[Path]:
        """
        Create worktrees from all schemas in the schema directory.
        
        Returns:
            List of paths to created worktrees
        """
        created = []
        
        for schema_file in self.config.schema_dir.glob("*.json"):
            with open(schema_file) as f:
                schema_data = json.load(f)
            
            # Reconstruct schema (simplified)
            hypothesis = Hypothesis(
                id=schema_data.get("hypothesis_id", "unknown"),
                statement=schema_data.get("hypothesis", ""),
                belief=BayesianBelief(prior=schema_data.get("prior_probability", 0.5)),
            )
            
            experiments = [
                Experiment(
                    id=exp.get("id", ""),
                    hypothesis_id=hypothesis.id,
                    description=exp.get("description", ""),
                    expected_outcome=exp.get("expected_outcome", ""),
                    success_criteria=exp.get("success_criteria", ""),
                )
                for exp in schema_data.get("experiments", [])
            ]
            
            schema = WorktreeSchema(
                schema_id=schema_data.get("schema_id", schema_file.stem),
                hypothesis=hypothesis,
                branch_name=schema_data.get("branch_name", f"experiment/{hypothesis.id}"),
                experiments=experiments,
            )
            
            try:
                path = self.create_worktree_from_schema(schema)
                created.append(path)
            except RuntimeError as e:
                print(f"Warning: {e}")
        
        return created
    
    def cleanup_worktree(self, schema_id: str) -> bool:
        """
        Remove a worktree.
        
        Args:
            schema_id: ID of the schema whose worktree to remove
        
        Returns:
            True if successful
        """
        if schema_id not in self.worktrees_created:
            return False
        
        worktree_path = self.worktrees_created[schema_id]
        
        try:
            self._run_git_command(["worktree", "remove", worktree_path, "--force"])
            del self.worktrees_created[schema_id]
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_evaluation_summary(self) -> dict:
        """Get summary of all evaluations performed."""
        return {
            "total_evidence": len(self.evidence),
            "evaluations": len(self.evaluation_history),
            "worktrees_created": len(self.worktrees_created),
            "evidence_by_type": {
                "supporting": sum(1 for e in self.evidence.values() if e.type == EvidenceType.SUPPORTING),
                "contradicting": sum(1 for e in self.evidence.values() if e.type == EvidenceType.CONTRADICTING),
                "neutral": sum(1 for e in self.evidence.values() if e.type == EvidenceType.NEUTRAL),
            },
            "recent_evaluations": self.evaluation_history[-10:],
        }
    
    def batch_update_beliefs(
        self,
        hypothesis: Hypothesis,
        evidence_list: list[Evidence],
    ) -> BayesianBelief:
        """
        Update beliefs with multiple pieces of evidence.
        
        Args:
            hypothesis: The hypothesis to update
            evidence_list: List of evidence to incorporate
        
        Returns:
            Final updated belief
        """
        current_belief = hypothesis.belief
        
        for evidence in evidence_list:
            current_belief = self.update_belief(hypothesis, evidence)
        
        return current_belief
