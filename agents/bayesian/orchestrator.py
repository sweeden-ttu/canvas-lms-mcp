"""
Bayesian Orchestrator

Coordinates the three Bayesian reasoning agents:
1. Hypothesis Generator - Creates hypotheses and worktree schemas
2. Evidence Evaluator - Evaluates evidence and creates worktrees
3. Backwards Reasoner - Finds causes from effects using inverse probability
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .hypothesis_generator import HypothesisGeneratorAgent, GeneratorConfig
from .evidence_evaluator import EvidenceEvaluatorAgent, EvaluatorConfig
from .backwards_reasoner import BackwardsReasonerAgent, ReasonerConfig
from .schemas import (
    Hypothesis,
    Experiment,
    Evidence,
    WorktreeSchema,
    EvidenceType,
)


@dataclass
class OrchestratorConfig:
    """Configuration for the Bayesian Orchestrator."""
    generator_config: GeneratorConfig = field(default_factory=GeneratorConfig)
    evaluator_config: EvaluatorConfig = field(default_factory=EvaluatorConfig)
    reasoner_config: ReasonerConfig = field(default_factory=ReasonerConfig)
    output_dir: Path = field(default_factory=lambda: Path("bayesian_output"))
    enable_backwards_reasoning: bool = True
    auto_create_worktrees: bool = False


class BayesianOrchestrator:
    """
    Orchestrates the three Bayesian reasoning agents.
    
    Workflow:
    1. Backwards Reasoner identifies potential causes from observations
    2. Hypothesis Generator creates hypotheses and worktree schemas
    3. Evidence Evaluator runs experiments and updates beliefs
    4. Cycle continues with refined hypotheses
    
    Architecture:
    
    ┌─────────────────────────────────────────────────────────────────┐
    │                    Bayesian Orchestrator                         │
    ├─────────────────┬─────────────────────┬─────────────────────────┤
    │   Hypothesis    │     Evidence        │      Backwards          │
    │   Generator     │     Evaluator       │      Reasoner           │
    │   (Agent 1)     │     (Agent 2)       │      (Agent 3)          │
    ├─────────────────┼─────────────────────┼─────────────────────────┤
    │ - Hypotheses    │ - Evaluate evidence │ - Find causes           │
    │ - Experiments   │ - Update beliefs    │ - Conditional vars      │
    │ - Predictions   │ - Verify results    │ - Inverse probability   │
    │ - WT Schemas    │ - Create worktrees  │ - Suggest hypotheses    │
    └─────────────────┴─────────────────────┴─────────────────────────┘
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        
        # Initialize agents
        self.generator = HypothesisGeneratorAgent(self.config.generator_config)
        self.evaluator = EvidenceEvaluatorAgent(self.config.evaluator_config)
        self.reasoner = BackwardsReasonerAgent(self.config.reasoner_config)
        
        # Shared state
        self.hypotheses: dict[str, Hypothesis] = {}
        self.experiments: dict[str, Experiment] = {}
        self.evidence: dict[str, Evidence] = {}
        self.schemas: dict[str, WorktreeSchema] = {}
        
        # History
        self.reasoning_history: list[dict] = []
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # Main Reasoning Workflow
    # =========================================================================
    
    def reason_from_observation(
        self,
        observation: str,
        observation_vars: Optional[dict[str, str]] = None,
    ) -> dict:
        """
        Complete reasoning workflow from observation.
        
        1. Use Backwards Reasoner to find potential causes
        2. Generate hypotheses for each potential cause
        3. Design experiments for each hypothesis
        4. Create worktree schemas for parallel exploration
        
        Args:
            observation: Natural language description of observation
            observation_vars: Optional structured observation {var: value}
        
        Returns:
            Reasoning result with hypotheses and schemas
        """
        result = {
            "observation": observation,
            "timestamp": datetime.utcnow().isoformat(),
            "backwards_analysis": None,
            "hypotheses": [],
            "schemas": [],
        }
        
        # Step 1: Backwards reasoning to find potential causes
        if self.config.enable_backwards_reasoning and observation_vars:
            explanation = self.reasoner.explain_observation(observation_vars)
            result["backwards_analysis"] = explanation
            
            # Get hypothesis suggestions from backwards reasoner
            for effect_var, effect_value in observation_vars.items():
                suggestions = self.reasoner.suggest_hypotheses_from_effect(
                    effect_var, effect_value
                )
                
                # Step 2: Generate hypotheses from suggestions
                for suggestion in suggestions:
                    hypothesis = self.generator.generate_hypothesis(
                        statement=suggestion["hypothesis_statement"],
                        rationale=suggestion["supporting_reasoning"],
                        predictions=[f"If {suggestion['cause_variable']} is manipulated, {effect_var} will change"],
                        prior=suggestion["prior_probability"],
                    )
                    
                    # Design experiments
                    for exp_suggestion in suggestion["suggested_experiments"]:
                        self.generator.design_experiment(
                            hypothesis=hypothesis,
                            description=exp_suggestion,
                            expected_outcome=f"{effect_var} changes as predicted",
                            success_criteria="Statistically significant change",
                        )
                    
                    # Create worktree schema
                    schema = self.generator.create_worktree_schema(hypothesis)
                    
                    # Store
                    self.hypotheses[hypothesis.id] = hypothesis
                    self.schemas[schema.schema_id] = schema
                    
                    result["hypotheses"].append({
                        "id": hypothesis.id,
                        "statement": hypothesis.statement,
                        "prior": hypothesis.belief.prior,
                    })
                    result["schemas"].append({
                        "id": schema.schema_id,
                        "branch": schema.branch_name,
                    })
        else:
            # Fallback: Generate hypotheses directly from observation
            hypotheses = self.generator.generate_alternative_hypotheses(observation)
            
            for hypothesis in hypotheses:
                self.generator.design_experiment(
                    hypothesis=hypothesis,
                    description=f"Test hypothesis: {hypothesis.statement}",
                    expected_outcome="Observation explained",
                    success_criteria="Hypothesis predictions match reality",
                )
                
                schema = self.generator.create_worktree_schema(hypothesis)
                
                self.hypotheses[hypothesis.id] = hypothesis
                self.schemas[schema.schema_id] = schema
                
                result["hypotheses"].append({
                    "id": hypothesis.id,
                    "statement": hypothesis.statement,
                    "prior": hypothesis.belief.prior,
                })
                result["schemas"].append({
                    "id": schema.schema_id,
                    "branch": schema.branch_name,
                })
        
        # Record in history
        self.reasoning_history.append(result)
        
        # Auto-create worktrees if enabled
        if self.config.auto_create_worktrees:
            for schema_id in [s["id"] for s in result["schemas"]]:
                schema = self.schemas.get(schema_id)
                if schema:
                    try:
                        self.evaluator.create_worktree_from_schema(schema)
                    except RuntimeError as e:
                        result.setdefault("warnings", []).append(str(e))
        
        return result
    
    def evaluate_experiment_result(
        self,
        experiment_id: str,
        observation: str,
        matches_prediction: bool,
        strength: float = 0.7,
        data: Optional[dict] = None,
    ) -> dict:
        """
        Evaluate an experimental result and update beliefs.
        
        Args:
            experiment_id: ID of the experiment
            observation: What was observed
            matches_prediction: Did it match the expected outcome?
            strength: Strength of evidence
            data: Raw data
        
        Returns:
            Evaluation result with updated beliefs
        """
        # Find experiment
        experiment = self.generator.experiments.get(experiment_id)
        if not experiment:
            return {"error": f"Experiment {experiment_id} not found"}
        
        # Evaluate evidence
        evidence = self.evaluator.evaluate_evidence(
            experiment=experiment,
            observation=observation,
            matches_prediction=matches_prediction,
            strength=strength,
            data=data,
        )
        
        # Find hypothesis
        hypothesis = self.hypotheses.get(experiment.hypothesis_id)
        if not hypothesis:
            hypothesis = self.generator.hypotheses.get(experiment.hypothesis_id)
        
        if not hypothesis:
            return {"error": f"Hypothesis for experiment {experiment_id} not found"}
        
        # Update belief
        updated_belief = self.evaluator.update_belief(hypothesis, evidence)
        
        # Update backwards reasoner
        if self.config.enable_backwards_reasoning:
            self.reasoner.update_from_evidence(evidence, hypothesis)
        
        # Store evidence
        self.evidence[evidence.id] = evidence
        
        result = {
            "experiment_id": experiment_id,
            "hypothesis_id": hypothesis.id,
            "evidence_id": evidence.id,
            "evidence_type": evidence.type.value,
            "prior": hypothesis.belief.prior,
            "posterior": updated_belief.posterior,
            "status": hypothesis.status.value,
            "belief_change": (updated_belief.posterior or 0) - hypothesis.belief.prior,
        }
        
        # Check if we need refined hypotheses
        if hypothesis.status.value == "inconclusive":
            result["suggestion"] = "Consider refining the hypothesis"
            result["relevant_variables"] = self.reasoner.find_conditional_variables(
                target_var=experiment.hypothesis_id,
                observed_vars=[evidence.id],
            )
        
        return result
    
    def refine_hypothesis(
        self,
        original_id: str,
        evidence_id: str,
        refinement: str,
    ) -> dict:
        """
        Create a refined hypothesis based on evidence.
        
        Args:
            original_id: ID of the original hypothesis
            evidence_id: ID of the evidence prompting refinement
            refinement: The refined hypothesis statement
        
        Returns:
            New hypothesis and schema
        """
        original = self.hypotheses.get(original_id) or self.generator.hypotheses.get(original_id)
        evidence = self.evidence.get(evidence_id)
        
        if not original:
            return {"error": f"Hypothesis {original_id} not found"}
        if not evidence:
            return {"error": f"Evidence {evidence_id} not found"}
        
        # Create refined hypothesis
        refined = self.evaluator.form_refined_hypothesis(original, evidence, refinement)
        
        # Create schema for refined hypothesis
        schema = self.generator.create_worktree_schema(refined)
        
        # Store
        self.hypotheses[refined.id] = refined
        self.schemas[schema.schema_id] = schema
        
        return {
            "original_id": original_id,
            "refined_id": refined.id,
            "statement": refined.statement,
            "prior": refined.belief.prior,
            "schema_id": schema.schema_id,
            "branch": schema.branch_name,
        }
    
    # =========================================================================
    # Causal Network Setup
    # =========================================================================
    
    def setup_causal_network(
        self,
        variables: list[dict],
        causal_links: list[dict],
    ) -> None:
        """
        Set up the causal network for backwards reasoning.
        
        Args:
            variables: List of {name, description, values, priors}
            causal_links: List of {cause, effect, strength, conditionals}
        """
        for var in variables:
            self.reasoner.add_variable(
                name=var["name"],
                description=var.get("description", ""),
                possible_values=var.get("values", ["true", "false"]),
                prior_distribution=var.get("priors"),
            )
        
        for link in causal_links:
            self.reasoner.add_causal_link(
                cause=link["cause"],
                effect=link["effect"],
                strength=link.get("strength", 0.5),
                conditional_probs=link.get("conditionals"),
            )
    
    def query_backwards(
        self,
        effect_var: str,
        effect_value: str,
    ) -> dict:
        """
        Query for causes of an observed effect.
        
        Args:
            effect_var: The observed variable
            effect_value: The observed value
        
        Returns:
            Backwards query results with ranked causes
        """
        query = self.reasoner.query_causes(effect_var, effect_value)
        
        return {
            "query_id": query.query_id,
            "effect": f"{effect_var} = {effect_value}",
            "causes": query.results,
            "reasoning": query.reasoning_chain,
            "conditional_variables": self.reasoner.find_conditional_variables(
                target_var=effect_var,
                observed_vars=[],
            ),
        }
    
    # =========================================================================
    # Worktree Management
    # =========================================================================
    
    def create_all_worktrees(self) -> list[str]:
        """Create worktrees for all pending schemas."""
        created = []
        
        for schema_id, schema in self.schemas.items():
            if schema.status == "pending":
                try:
                    path = self.evaluator.create_worktree_from_schema(schema)
                    created.append(str(path))
                except RuntimeError as e:
                    print(f"Warning: {e}")
        
        return created
    
    def cleanup_all_worktrees(self) -> int:
        """Remove all created worktrees."""
        count = 0
        for schema_id in list(self.evaluator.worktrees_created.keys()):
            if self.evaluator.cleanup_worktree(schema_id):
                count += 1
        return count
    
    # =========================================================================
    # Reporting
    # =========================================================================
    
    def get_status(self) -> dict:
        """Get current status of all agents."""
        return {
            "hypotheses": {
                "total": len(self.hypotheses),
                "by_status": self._count_by_status(),
            },
            "experiments": {
                "total": len(self.generator.experiments),
            },
            "evidence": {
                "total": len(self.evidence),
                "by_type": self._count_evidence_by_type(),
            },
            "schemas": {
                "total": len(self.schemas),
                "worktrees_created": len(self.evaluator.worktrees_created),
            },
            "causal_network": self.reasoner.get_network_summary(),
            "reasoning_steps": len(self.reasoning_history),
        }
    
    def _count_by_status(self) -> dict:
        """Count hypotheses by status."""
        counts = {}
        for h in self.hypotheses.values():
            status = h.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def _count_evidence_by_type(self) -> dict:
        """Count evidence by type."""
        counts = {}
        for e in self.evidence.values():
            etype = e.type.value
            counts[etype] = counts.get(etype, 0) + 1
        return counts
    
    def export_report(self, path: Optional[Path] = None) -> Path:
        """Export a full reasoning report."""
        if path is None:
            path = self.config.output_dir / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "status": self.get_status(),
            "hypotheses": [
                {
                    "id": h.id,
                    "statement": h.statement,
                    "prior": h.belief.prior,
                    "posterior": h.belief.posterior,
                    "status": h.status.value,
                }
                for h in self.hypotheses.values()
            ],
            "schemas": [
                s.to_dict() for s in self.schemas.values()
            ],
            "causal_network": self.reasoner.get_network_summary(),
            "reasoning_history": self.reasoning_history,
        }
        
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        
        return path
