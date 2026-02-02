"""
Hypothesis Generator Agent (Agent 1)

Responsibilities:
- Generate testable hypotheses from observations
- Design experiments to test hypotheses
- Predict expected outcomes with confidence levels
- Create worktree schemas for parallel hypothesis exploration
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
)


@dataclass
class GeneratorConfig:
    """Configuration for the Hypothesis Generator Agent."""
    min_prior: float = 0.1
    max_prior: float = 0.9
    default_prior: float = 0.5
    min_experiments_per_hypothesis: int = 1
    max_experiments_per_hypothesis: int = 5
    schema_output_dir: Path = field(default_factory=lambda: Path("worktree_schemas"))


class HypothesisGeneratorAgent:
    """
    Agent 1: Generates hypotheses, designs experiments, and creates worktree schemas.
    
    This agent uses Bayesian reasoning to:
    1. Generate testable hypotheses from observations
    2. Assign prior probabilities based on background knowledge
    3. Design experiments with clear success criteria
    4. Create worktree schemas for parallel exploration
    """
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        self.hypotheses: dict[str, Hypothesis] = {}
        self.experiments: dict[str, Experiment] = {}
        self.schemas: dict[str, WorktreeSchema] = {}
        
        # Ensure output directory exists
        self.config.schema_output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_hypothesis(
        self,
        statement: str,
        rationale: str = "",
        predictions: Optional[list[str]] = None,
        prior: Optional[float] = None,
        parent_id: Optional[str] = None,
    ) -> Hypothesis:
        """
        Generate a new hypothesis with Bayesian prior.
        
        Args:
            statement: The hypothesis statement (should be testable)
            rationale: Reasoning behind the hypothesis
            predictions: Observable predictions if hypothesis is true
            prior: Prior probability (0-1), defaults to 0.5
            parent_id: ID of parent hypothesis if this is a refinement
        
        Returns:
            Hypothesis object with assigned prior probability
        """
        # Validate and set prior
        if prior is None:
            prior = self.config.default_prior
        prior = max(self.config.min_prior, min(self.config.max_prior, prior))
        
        # Create belief with prior
        belief = BayesianBelief(prior=prior)
        
        # Create hypothesis
        hypothesis = Hypothesis(
            statement=statement,
            rationale=rationale,
            predictions=predictions or [],
            belief=belief,
            parent_hypothesis_id=parent_id,
        )
        
        # Store hypothesis
        self.hypotheses[hypothesis.id] = hypothesis
        
        return hypothesis
    
    def generate_alternative_hypotheses(
        self,
        observation: str,
        num_alternatives: int = 3,
    ) -> list[Hypothesis]:
        """
        Generate multiple alternative hypotheses for an observation.
        
        Uses the principle of multiple working hypotheses to avoid
        confirmation bias.
        
        Args:
            observation: The observation to explain
            num_alternatives: Number of alternative hypotheses to generate
        
        Returns:
            List of alternative hypotheses with priors summing to ~1
        """
        hypotheses = []
        
        # Distribute prior probability across alternatives
        # Use slightly unequal distribution to reflect varying plausibility
        base_prior = 1.0 / (num_alternatives + 1)  # Leave room for "other"
        
        for i in range(num_alternatives):
            # Vary prior slightly
            prior = base_prior * (1 + (0.2 * (i - num_alternatives // 2)))
            prior = max(0.1, min(0.5, prior))
            
            hypothesis = self.generate_hypothesis(
                statement=f"Alternative {i + 1} for: {observation}",
                rationale=f"Generated as alternative explanation #{i + 1}",
                prior=prior,
            )
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def design_experiment(
        self,
        hypothesis: Hypothesis,
        description: str,
        expected_outcome: str,
        success_criteria: str,
        methodology: str = "",
        null_outcome: str = "",
    ) -> Experiment:
        """
        Design an experiment to test a hypothesis.
        
        Args:
            hypothesis: The hypothesis to test
            description: Description of the experiment
            expected_outcome: What we expect to observe if H is true
            success_criteria: Measurable criteria for success
            methodology: How to conduct the experiment
            null_outcome: What we expect if H is false
        
        Returns:
            Experiment object linked to the hypothesis
        """
        experiment = Experiment(
            hypothesis_id=hypothesis.id,
            description=description,
            methodology=methodology,
            expected_outcome=expected_outcome,
            success_criteria=success_criteria,
            null_outcome=null_outcome or f"Not: {expected_outcome}",
        )
        
        # Link experiment to hypothesis
        hypothesis.experiment_ids.append(experiment.id)
        hypothesis.updated_at = datetime.utcnow()
        
        # Store experiment
        self.experiments[experiment.id] = experiment
        
        return experiment
    
    def design_experiment_battery(
        self,
        hypothesis: Hypothesis,
        experiment_specs: list[dict],
    ) -> list[Experiment]:
        """
        Design multiple experiments for a hypothesis.
        
        Args:
            hypothesis: The hypothesis to test
            experiment_specs: List of experiment specifications
        
        Returns:
            List of designed experiments
        """
        experiments = []
        
        for spec in experiment_specs[:self.config.max_experiments_per_hypothesis]:
            experiment = self.design_experiment(
                hypothesis=hypothesis,
                description=spec.get("description", ""),
                expected_outcome=spec.get("expected_outcome", ""),
                success_criteria=spec.get("success_criteria", ""),
                methodology=spec.get("methodology", ""),
                null_outcome=spec.get("null_outcome", ""),
            )
            experiments.append(experiment)
        
        return experiments
    
    def create_worktree_schema(
        self,
        hypothesis: Hypothesis,
        experiments: Optional[list[Experiment]] = None,
    ) -> WorktreeSchema:
        """
        Create a worktree schema for hypothesis exploration.
        
        The schema defines how to create a git worktree for parallel
        exploration of the hypothesis.
        
        Args:
            hypothesis: The hypothesis to explore
            experiments: Experiments to include (defaults to all linked)
        
        Returns:
            WorktreeSchema object
        """
        # Get experiments
        if experiments is None:
            experiments = [
                self.experiments[exp_id]
                for exp_id in hypothesis.experiment_ids
                if exp_id in self.experiments
            ]
        
        # Create schema
        schema = WorktreeSchema.from_hypothesis(hypothesis)
        schema.experiments = experiments
        
        # Store schema
        self.schemas[schema.schema_id] = schema
        
        # Save schema to file
        self._save_schema(schema)
        
        return schema
    
    def _save_schema(self, schema: WorktreeSchema) -> Path:
        """Save worktree schema to JSON file."""
        schema_path = self.config.schema_output_dir / f"{schema.schema_id}.json"
        
        with open(schema_path, "w") as f:
            json.dump(schema.to_dict(), f, indent=2)
        
        return schema_path
    
    def predict_outcomes(
        self,
        hypothesis: Hypothesis,
    ) -> dict[str, dict]:
        """
        Generate outcome predictions for a hypothesis.
        
        Returns predictions for both hypothesis being true and false,
        with associated probabilities.
        
        Args:
            hypothesis: The hypothesis to generate predictions for
        
        Returns:
            Dictionary with predictions and probabilities
        """
        prior = hypothesis.belief.prior
        
        predictions = {
            "if_true": {
                "probability": prior,
                "outcomes": hypothesis.predictions,
                "experiments": [
                    {
                        "id": self.experiments[exp_id].id,
                        "expected": self.experiments[exp_id].expected_outcome,
                    }
                    for exp_id in hypothesis.experiment_ids
                    if exp_id in self.experiments
                ],
            },
            "if_false": {
                "probability": 1 - prior,
                "outcomes": [f"Not: {pred}" for pred in hypothesis.predictions],
                "experiments": [
                    {
                        "id": self.experiments[exp_id].id,
                        "expected": self.experiments[exp_id].null_outcome,
                    }
                    for exp_id in hypothesis.experiment_ids
                    if exp_id in self.experiments
                ],
            },
        }
        
        return predictions
    
    def get_all_schemas(self) -> list[WorktreeSchema]:
        """Get all worktree schemas."""
        return list(self.schemas.values())
    
    def get_pending_hypotheses(self) -> list[Hypothesis]:
        """Get all hypotheses pending testing."""
        return [
            h for h in self.hypotheses.values()
            if h.status == HypothesisStatus.PENDING
        ]
    
    def export_all_schemas(self) -> list[Path]:
        """Export all schemas to files."""
        paths = []
        for schema in self.schemas.values():
            path = self._save_schema(schema)
            paths.append(path)
        return paths
    
    def create_hypothesis_tree(
        self,
        root_observation: str,
        depth: int = 2,
        breadth: int = 2,
    ) -> dict:
        """
        Create a tree of hypotheses for exploration.
        
        Args:
            root_observation: Initial observation
            depth: Depth of hypothesis refinement
            breadth: Number of alternatives at each level
        
        Returns:
            Tree structure of hypotheses
        """
        def build_level(observation: str, level: int, parent_id: Optional[str] = None) -> list[dict]:
            if level > depth:
                return []
            
            hypotheses = self.generate_alternative_hypotheses(observation, breadth)
            
            tree = []
            for h in hypotheses:
                if parent_id:
                    h.parent_hypothesis_id = parent_id
                
                # Create schema for this hypothesis
                schema = self.create_worktree_schema(h)
                
                node = {
                    "hypothesis": h,
                    "schema": schema,
                    "children": build_level(
                        f"Given {h.statement}, what follows?",
                        level + 1,
                        h.id,
                    ),
                }
                tree.append(node)
            
            return tree
        
        return {
            "observation": root_observation,
            "hypotheses": build_level(root_observation, 1),
        }
