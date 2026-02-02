"""
Backwards Probability Conditional Agent (Agent 3)

Responsibilities:
- Perform backwards (abductive) reasoning from effects to causes
- Calculate conditional probabilities P(Cause|Effect)
- Find conditional variables for backwards reasoning
- Build causal graphs for inference
- Support hypothesis generation through inverse probability
"""

import math
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict

from .schemas import (
    Hypothesis,
    Evidence,
    BayesianBelief,
    EvidenceType,
)


@dataclass
class ConditionalVariable:
    """A variable in the conditional probability network."""
    
    name: str
    description: str = ""
    possible_values: list[str] = field(default_factory=lambda: ["true", "false"])
    prior_distribution: dict[str, float] = field(default_factory=dict)
    observed_value: Optional[str] = None
    is_observed: bool = False
    
    def __post_init__(self):
        # Initialize uniform prior if not provided
        if not self.prior_distribution:
            n = len(self.possible_values)
            self.prior_distribution = {v: 1.0 / n for v in self.possible_values}
    
    def set_observed(self, value: str) -> None:
        """Set this variable as observed with a specific value."""
        if value in self.possible_values:
            self.observed_value = value
            self.is_observed = True
    
    def get_prior(self, value: str) -> float:
        """Get prior probability for a value."""
        return self.prior_distribution.get(value, 0.0)


@dataclass
class ConditionalProbability:
    """Represents P(Effect|Cause) - conditional probability table entry."""
    
    effect_var: str
    effect_value: str
    cause_var: str
    cause_value: str
    probability: float  # P(effect_value | cause_value)
    
    def __repr__(self):
        return f"P({self.effect_var}={self.effect_value}|{self.cause_var}={self.cause_value}) = {self.probability:.4f}"


@dataclass
class CausalLink:
    """A causal link between two variables."""
    
    cause: str
    effect: str
    strength: float = 0.5  # How strongly cause influences effect
    conditional_probs: dict[tuple[str, str], float] = field(default_factory=dict)
    # Key: (cause_value, effect_value), Value: P(effect_value|cause_value)


@dataclass
class BackwardsQuery:
    """A query for backwards reasoning."""
    
    query_id: str
    effect_var: str
    effect_value: str
    candidate_causes: list[str]
    results: dict[str, float] = field(default_factory=dict)  # cause -> P(cause|effect)
    reasoning_chain: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasonerConfig:
    """Configuration for the Backwards Reasoner Agent."""
    min_probability: float = 0.001
    max_causes_to_consider: int = 10
    inference_iterations: int = 100
    convergence_threshold: float = 0.0001


class BackwardsReasonerAgent:
    """
    Agent 3: Performs backwards probability reasoning.
    
    Uses Bayes' theorem in reverse to reason from effects to causes:
    P(Cause|Effect) = P(Effect|Cause) * P(Cause) / P(Effect)
    
    This agent:
    1. Builds causal graphs from domain knowledge
    2. Calculates inverse conditional probabilities
    3. Finds the most likely causes given observed effects
    4. Identifies important conditional variables
    5. Supports abductive inference for hypothesis generation
    """
    
    def __init__(self, config: Optional[ReasonerConfig] = None):
        self.config = config or ReasonerConfig()
        self.variables: dict[str, ConditionalVariable] = {}
        self.causal_links: dict[tuple[str, str], CausalLink] = {}
        self.conditional_tables: dict[str, list[ConditionalProbability]] = defaultdict(list)
        self.queries: dict[str, BackwardsQuery] = {}
        self.inference_cache: dict[str, float] = {}
    
    # =========================================================================
    # Variable and Causal Structure Management
    # =========================================================================
    
    def add_variable(
        self,
        name: str,
        description: str = "",
        possible_values: Optional[list[str]] = None,
        prior_distribution: Optional[dict[str, float]] = None,
    ) -> ConditionalVariable:
        """
        Add a variable to the causal network.
        
        Args:
            name: Variable name (unique identifier)
            description: Human-readable description
            possible_values: List of possible values (default: ["true", "false"])
            prior_distribution: Prior probabilities for each value
        
        Returns:
            The created ConditionalVariable
        """
        var = ConditionalVariable(
            name=name,
            description=description,
            possible_values=possible_values or ["true", "false"],
            prior_distribution=prior_distribution or {},
        )
        self.variables[name] = var
        return var
    
    def add_causal_link(
        self,
        cause: str,
        effect: str,
        strength: float = 0.5,
        conditional_probs: Optional[dict[tuple[str, str], float]] = None,
    ) -> CausalLink:
        """
        Add a causal link between two variables.
        
        Args:
            cause: Name of the cause variable
            effect: Name of the effect variable
            strength: Strength of causal relationship (0-1)
            conditional_probs: P(effect_value|cause_value) for each combination
        
        Returns:
            The created CausalLink
        """
        # Ensure variables exist
        if cause not in self.variables:
            self.add_variable(cause)
        if effect not in self.variables:
            self.add_variable(effect)
        
        link = CausalLink(
            cause=cause,
            effect=effect,
            strength=strength,
            conditional_probs=conditional_probs or {},
        )
        self.causal_links[(cause, effect)] = link
        
        # Build conditional probability table
        if conditional_probs:
            for (cause_val, effect_val), prob in conditional_probs.items():
                self._upsert_conditional_probability(
                    effect_var=effect,
                    effect_value=effect_val,
                    cause_var=cause,
                    cause_value=cause_val,
                    probability=prob,
                )
        
        return link
    
    def set_conditional_probability(
        self,
        effect_var: str,
        effect_value: str,
        cause_var: str,
        cause_value: str,
        probability: float,
    ) -> None:
        """
        Set a specific conditional probability P(effect|cause).
        
        Args:
            effect_var: Effect variable name
            effect_value: Effect variable value
            cause_var: Cause variable name
            cause_value: Cause variable value
            probability: P(effect_value|cause_value)
        """
        # Update causal link
        link_key = (cause_var, effect_var)
        if link_key in self.causal_links:
            self.causal_links[link_key].conditional_probs[(cause_value, effect_value)] = probability
        
        # Update conditional table (upsert: update if exists, insert if not)
        self._upsert_conditional_probability(
            effect_var=effect_var,
            effect_value=effect_value,
            cause_var=cause_var,
            cause_value=cause_value,
            probability=probability,
        )
        
        # Clear cache
        self.inference_cache.clear()
    
    def _upsert_conditional_probability(
        self,
        effect_var: str,
        effect_value: str,
        cause_var: str,
        cause_value: str,
        probability: float,
    ) -> None:
        """
        Update or insert a conditional probability entry.
        
        Searches for existing entry with matching (effect_var, effect_value,
        cause_var, cause_value) and updates it. If not found, inserts new entry.
        This prevents stale entries from accumulating in the conditional tables.
        """
        entries = self.conditional_tables[effect_var]
        
        # Search for existing entry and update it
        for cp in entries:
            if (cp.cause_var == cause_var and 
                cp.cause_value == cause_value and 
                cp.effect_value == effect_value):
                cp.probability = probability
                return
        
        # No existing entry found, insert new one
        entries.append(
            ConditionalProbability(
                effect_var=effect_var,
                effect_value=effect_value,
                cause_var=cause_var,
                cause_value=cause_value,
                probability=probability,
            )
        )
    
    # =========================================================================
    # Core Backwards Reasoning
    # =========================================================================
    
    def calculate_backwards_probability(
        self,
        cause_var: str,
        cause_value: str,
        effect_var: str,
        effect_value: str,
    ) -> float:
        """
        Calculate P(Cause|Effect) using Bayes' theorem.
        
        P(Cause|Effect) = P(Effect|Cause) * P(Cause) / P(Effect)
        
        Args:
            cause_var: Name of the cause variable
            cause_value: Value of the cause
            effect_var: Name of the effect variable
            effect_value: Value of the effect (observed)
        
        Returns:
            P(cause_value|effect_value)
        """
        # Check cache
        cache_key = f"{cause_var}={cause_value}|{effect_var}={effect_value}"
        if cache_key in self.inference_cache:
            return self.inference_cache[cache_key]
        
        # Get P(Effect|Cause) - likelihood
        likelihood = self._get_likelihood(effect_var, effect_value, cause_var, cause_value)
        
        # Get P(Cause) - prior
        prior = self._get_prior(cause_var, cause_value)
        
        # Calculate P(Effect) - marginal (evidence)
        marginal = self._calculate_marginal(effect_var, effect_value)
        
        # Apply Bayes' theorem
        if marginal > 0:
            posterior = (likelihood * prior) / marginal
        else:
            posterior = prior  # Fall back to prior if marginal is zero
        
        # Ensure valid probability
        posterior = max(self.config.min_probability, min(1.0, posterior))
        
        # Cache result
        self.inference_cache[cache_key] = posterior
        
        return posterior
    
    def _get_likelihood(
        self,
        effect_var: str,
        effect_value: str,
        cause_var: str,
        cause_value: str,
    ) -> float:
        """Get P(Effect|Cause) from conditional tables."""
        for cp in self.conditional_tables.get(effect_var, []):
            if (cp.cause_var == cause_var and 
                cp.cause_value == cause_value and 
                cp.effect_value == effect_value):
                return cp.probability
        
        # Default: use causal link strength or 0.5
        link_key = (cause_var, effect_var)
        if link_key in self.causal_links:
            link = self.causal_links[link_key]
            prob = link.conditional_probs.get((cause_value, effect_value))
            if prob is not None:
                return prob
            # Infer from strength
            if cause_value == "true" and effect_value == "true":
                return link.strength
            elif cause_value == "false" and effect_value == "false":
                return link.strength
            else:
                return 1 - link.strength
        
        return 0.5  # Uniform if unknown
    
    def _get_prior(self, var: str, value: str) -> float:
        """Get prior probability P(var=value)."""
        if var in self.variables:
            return self.variables[var].get_prior(value)
        return 0.5
    
    def _calculate_marginal(self, effect_var: str, effect_value: str) -> float:
        """
        Calculate marginal probability P(Effect) by summing over all causes.
        
        P(Effect) = Σ P(Effect|Cause_i) * P(Cause_i)
        """
        marginal = 0.0
        
        # Find all causes of this effect
        causes = self._get_causes(effect_var)
        
        if not causes:
            # No known causes, use prior
            return self._get_prior(effect_var, effect_value)
        
        for cause_var in causes:
            cause_variable = self.variables.get(cause_var)
            if cause_variable:
                for cause_value in cause_variable.possible_values:
                    likelihood = self._get_likelihood(effect_var, effect_value, cause_var, cause_value)
                    prior = self._get_prior(cause_var, cause_value)
                    marginal += likelihood * prior
        
        return max(self.config.min_probability, marginal)
    
    def _get_causes(self, effect_var: str) -> list[str]:
        """Get all cause variables for an effect."""
        causes = []
        for (cause, effect), link in self.causal_links.items():
            if effect == effect_var:
                causes.append(cause)
        return causes
    
    def _get_effects(self, cause_var: str) -> list[str]:
        """Get all effect variables for a cause."""
        effects = []
        for (cause, effect), link in self.causal_links.items():
            if cause == cause_var:
                effects.append(effect)
        return effects
    
    # =========================================================================
    # Finding Conditional Variables
    # =========================================================================
    
    def find_conditional_variables(
        self,
        target_var: str,
        observed_vars: list[str],
    ) -> list[dict]:
        """
        Find variables that are conditionally relevant given observations.
        
        Uses d-separation concepts to identify which variables affect
        the target given what's observed.
        
        Args:
            target_var: The variable we want to reason about
            observed_vars: Variables that have been observed
        
        Returns:
            List of relevant conditional variables with their relevance scores
        """
        relevant_vars = []
        
        for var_name, variable in self.variables.items():
            if var_name == target_var or var_name in observed_vars:
                continue
            
            # Calculate relevance based on causal structure
            relevance = self._calculate_relevance(var_name, target_var, observed_vars)
            
            if relevance > self.config.min_probability:
                relevant_vars.append({
                    "variable": var_name,
                    "description": variable.description,
                    "relevance": relevance,
                    "relationship": self._describe_relationship(var_name, target_var),
                    "is_cause": self._is_cause_of(var_name, target_var),
                    "is_effect": self._is_cause_of(target_var, var_name),
                })
        
        # Sort by relevance
        relevant_vars.sort(key=lambda x: x["relevance"], reverse=True)
        
        return relevant_vars[:self.config.max_causes_to_consider]
    
    def _calculate_relevance(
        self,
        var: str,
        target: str,
        observed: list[str],
    ) -> float:
        """Calculate how relevant a variable is to the target."""
        relevance = 0.0
        
        # Direct causal relationship
        if self._is_cause_of(var, target):
            relevance += 0.8
        elif self._is_cause_of(target, var):
            relevance += 0.6  # Effect can inform about cause
        
        # Common cause or effect
        for other_var in self.variables:
            if self._is_cause_of(other_var, var) and self._is_cause_of(other_var, target):
                relevance += 0.4  # Common cause (confounder)
            if self._is_cause_of(var, other_var) and self._is_cause_of(target, other_var):
                relevance += 0.3  # Common effect (collider)
        
        # Adjust based on observations: add a single bonus if connected to any observation
        # (avoiding exponential growth from repeated multiplication)
        connected_to_observation = any(
            self._is_cause_of(obs, var) or self._is_cause_of(var, obs)
            for obs in observed
        )
        if connected_to_observation:
            relevance += 0.2  # Flat bonus for being connected to observations
        
        return min(1.0, relevance)
    
    def _is_cause_of(self, potential_cause: str, potential_effect: str) -> bool:
        """Check if one variable is a cause of another."""
        return (potential_cause, potential_effect) in self.causal_links
    
    def _describe_relationship(self, var1: str, var2: str) -> str:
        """Describe the relationship between two variables."""
        if self._is_cause_of(var1, var2):
            return f"{var1} causes {var2}"
        elif self._is_cause_of(var2, var1):
            return f"{var1} is caused by {var2}"
        else:
            # Check for common ancestors or descendants
            causes_1 = set(self._get_causes(var1))
            causes_2 = set(self._get_causes(var2))
            common_causes = causes_1 & causes_2
            
            if common_causes:
                return f"Common cause: {', '.join(common_causes)}"
            
            effects_1 = set(self._get_effects(var1))
            effects_2 = set(self._get_effects(var2))
            common_effects = effects_1 & effects_2
            
            if common_effects:
                return f"Common effect: {', '.join(common_effects)}"
            
            return "No direct relationship"
    
    # =========================================================================
    # Backwards Queries
    # =========================================================================
    
    def query_causes(
        self,
        effect_var: str,
        effect_value: str,
    ) -> BackwardsQuery:
        """
        Query for the most likely causes of an observed effect.
        
        Args:
            effect_var: The observed effect variable
            effect_value: The observed value
        
        Returns:
            BackwardsQuery with ranked causes
        """
        query_id = f"bq-{len(self.queries)}-{effect_var}"
        
        # Find all potential causes
        candidate_causes = self._get_causes(effect_var)
        
        if not candidate_causes:
            # Use all variables as potential causes
            candidate_causes = [v for v in self.variables if v != effect_var]
        
        # Calculate backwards probability for each cause
        results = {}
        reasoning_chain = [f"Observed: {effect_var} = {effect_value}"]
        
        for cause_var in candidate_causes:
            cause_variable = self.variables.get(cause_var)
            if not cause_variable:
                continue
            
            # Calculate P(cause=true|effect) for binary variables
            # or find the most likely value
            best_value = None
            best_prob = 0.0
            
            for cause_value in cause_variable.possible_values:
                prob = self.calculate_backwards_probability(
                    cause_var, cause_value, effect_var, effect_value
                )
                if prob > best_prob:
                    best_prob = prob
                    best_value = cause_value
            
            results[cause_var] = best_prob
            reasoning_chain.append(
                f"P({cause_var}={best_value}|{effect_var}={effect_value}) = {best_prob:.4f}"
            )
        
        # Sort by probability
        sorted_causes = sorted(results.items(), key=lambda x: x[1], reverse=True)
        reasoning_chain.append(f"Most likely cause: {sorted_causes[0][0] if sorted_causes else 'unknown'}")
        
        query = BackwardsQuery(
            query_id=query_id,
            effect_var=effect_var,
            effect_value=effect_value,
            candidate_causes=candidate_causes,
            results=dict(sorted_causes),
            reasoning_chain=reasoning_chain,
        )
        
        self.queries[query_id] = query
        return query
    
    def explain_observation(
        self,
        observation: dict[str, str],
    ) -> dict:
        """
        Generate explanations for multiple observations.
        
        Args:
            observation: Dict of variable: observed_value
        
        Returns:
            Explanation with most likely causes for each observation
        """
        explanations = {}
        combined_causes = defaultdict(float)
        
        for var, value in observation.items():
            # Mark as observed
            if var in self.variables:
                self.variables[var].set_observed(value)
            
            # Query causes
            query = self.query_causes(var, value)
            explanations[var] = {
                "query": query,
                "top_causes": list(query.results.items())[:3],
            }
            
            # Combine cause probabilities
            for cause, prob in query.results.items():
                combined_causes[cause] += prob
        
        # Normalize combined causes
        total = sum(combined_causes.values())
        if total > 0:
            combined_causes = {k: v / total for k, v in combined_causes.items()}
        
        return {
            "observations": observation,
            "per_observation_explanations": explanations,
            "combined_most_likely_causes": dict(
                sorted(combined_causes.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
        }
    
    # =========================================================================
    # Integration with Other Agents
    # =========================================================================
    
    def suggest_hypotheses_from_effect(
        self,
        effect_var: str,
        effect_value: str,
        min_probability: float = 0.1,
    ) -> list[dict]:
        """
        Suggest hypotheses based on backwards reasoning from an effect.
        
        This helps Agent 1 (Hypothesis Generator) by providing
        probability-ranked cause hypotheses.
        
        Args:
            effect_var: The observed effect
            effect_value: The observed value
            min_probability: Minimum probability to include
        
        Returns:
            List of hypothesis suggestions with probabilities
        """
        query = self.query_causes(effect_var, effect_value)
        
        suggestions = []
        for cause, prob in query.results.items():
            if prob >= min_probability:
                cause_var = self.variables.get(cause)
                suggestions.append({
                    "hypothesis_statement": f"{cause} caused {effect_var}={effect_value}",
                    "cause_variable": cause,
                    "prior_probability": prob,
                    "supporting_reasoning": self._describe_relationship(cause, effect_var),
                    "suggested_experiments": self._suggest_experiments(cause, effect_var),
                })
        
        return suggestions
    
    def _suggest_experiments(self, cause: str, effect: str) -> list[str]:
        """Suggest experiments to test a cause-effect relationship."""
        return [
            f"Manipulate {cause} and observe changes in {effect}",
            f"Find natural variation in {cause} and correlate with {effect}",
            f"Look for mediating variables between {cause} and {effect}",
        ]
    
    def update_from_evidence(
        self,
        evidence: Evidence,
        hypothesis: Hypothesis,
    ) -> dict:
        """
        Update causal model based on new evidence.
        
        This helps Agent 2 (Evidence Evaluator) by updating
        conditional probabilities.
        
        Args:
            evidence: New evidence
            hypothesis: The hypothesis being tested
        
        Returns:
            Updated beliefs and conditional probabilities
        """
        # Extract cause-effect from hypothesis
        # This is a simplified extraction - in practice, use NLP
        updates = {
            "evidence_type": evidence.type.value,
            "strength": evidence.strength,
            "updates": [],
        }
        
        # Update relevant conditional probabilities
        if evidence.type == EvidenceType.SUPPORTING:
            # Increase likelihood of cause given effect
            update_factor = 1 + (evidence.strength * 0.5)
        elif evidence.type == EvidenceType.CONTRADICTING:
            # Decrease likelihood
            update_factor = 1 - (evidence.strength * 0.5)
        else:
            update_factor = 1.0
        
        # Apply updates to relevant links
        for (cause, effect), link in self.causal_links.items():
            if hypothesis.statement and (cause in hypothesis.statement or effect in hypothesis.statement):
                for key in link.conditional_probs:
                    old_prob = link.conditional_probs[key]
                    new_prob = max(0.01, min(0.99, old_prob * update_factor))
                    link.conditional_probs[key] = new_prob
                    updates["updates"].append({
                        "link": f"{cause} -> {effect}",
                        "old": old_prob,
                        "new": new_prob,
                    })
        
        # Clear cache
        self.inference_cache.clear()
        
        return updates
    
    def get_network_summary(self) -> dict:
        """Get summary of the causal network."""
        return {
            "variables": list(self.variables.keys()),
            "num_variables": len(self.variables),
            "num_causal_links": len(self.causal_links),
            "causal_links": [
                {
                    "cause": cause,
                    "effect": effect,
                    "strength": link.strength,
                }
                for (cause, effect), link in self.causal_links.items()
            ],
            "num_queries": len(self.queries),
            "cache_size": len(self.inference_cache),
        }
