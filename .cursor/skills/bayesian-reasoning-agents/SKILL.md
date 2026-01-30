---
name: bayesian-reasoning-agents
description: Implements three Bayesian sub-agents for hypothesis-driven development. Use when generating hypotheses, designing experiments, evaluating evidence, performing backwards reasoning from effects to causes, finding conditional variables, verifying results, or creating git worktree schemas. Agent 1 generates hypotheses and schemas; Agent 2 evaluates evidence and creates worktrees; Agent 3 performs backwards probability reasoning to find causes.
---

# Bayesian Reasoning Agents

Three-agent system for hypothesis-driven development using Bayesian reasoning and git worktrees.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Bayesian Orchestrator                             │
├───────────────────┬─────────────────────┬───────────────────────────────┤
│   Agent 1:        │   Agent 2:          │   Agent 3:                    │
│   Hypothesis      │   Evidence          │   Backwards                   │
│   Generator       │   Evaluator         │   Reasoner                    │
├───────────────────┼─────────────────────┼───────────────────────────────┤
│ - Hypotheses      │ - Evaluate evidence │ - P(Cause|Effect)             │
│ - Experiments     │ - Update beliefs    │ - Conditional variables       │
│ - Predictions     │ - Verify results    │ - Causal graphs               │
│ - WT Schemas      │ - Create worktrees  │ - Suggest hypotheses          │
└───────────────────┴─────────────────────┴───────────────────────────────┘
         │                    │                        │
         ▼                    ▼                        ▼
   worktree_schemas/    worktrees/branch-*     Causal Network
```

## Quick Start

```bash
uv add numpy scipy pydantic
```

```python
from agents.bayesian import (
    BayesianOrchestrator,
    OrchestratorConfig,
)

# Initialize orchestrator with all three agents
orchestrator = BayesianOrchestrator()

# Set up causal network for backwards reasoning
orchestrator.setup_causal_network(
    variables=[
        {"name": "bug_in_code", "description": "A bug exists in the code"},
        {"name": "test_failure", "description": "Tests are failing"},
        {"name": "recent_change", "description": "Recent code change"},
    ],
    causal_links=[
        {"cause": "bug_in_code", "effect": "test_failure", "strength": 0.8},
        {"cause": "recent_change", "effect": "bug_in_code", "strength": 0.6},
    ]
)

# Reason from observation
result = orchestrator.reason_from_observation(
    observation="Tests started failing after deployment",
    observation_vars={"test_failure": "true"}
)

print(result["hypotheses"])
```

## Agent 1: Hypothesis Generator

**Responsibilities:**
- Generate testable hypotheses from observations
- Assign prior probabilities using domain knowledge
- Design experiments with success criteria
- Create worktree schemas for parallel exploration

**Key Methods:**

```python
from agents.bayesian import HypothesisGeneratorAgent

generator = HypothesisGeneratorAgent()

# Generate a hypothesis with prior probability
hypothesis = generator.generate_hypothesis(
    statement="The performance regression is caused by the new caching layer",
    rationale="Caching was recently modified and correlates with slowdown",
    predictions=["Disabling cache improves performance", "Cache hit ratio is abnormal"],
    prior=0.6,  # 60% prior probability
)

# Design experiment to test hypothesis
experiment = generator.design_experiment(
    hypothesis=hypothesis,
    description="Benchmark with cache disabled",
    expected_outcome="Latency returns to baseline",
    success_criteria="p95 latency < 100ms",
)

# Create worktree schema for parallel exploration
schema = generator.create_worktree_schema(hypothesis)
```

## Agent 2: Evidence Evaluator

**Responsibilities:**
- Evaluate experimental evidence
- Update beliefs using Bayes' theorem: P(H|E) = P(E|H) * P(H) / P(E)
- Form refined hypotheses when results are inconclusive
- Create git worktrees from schemas for parallel exploration

**Key Methods:**

```python
from agents.bayesian import EvidenceEvaluatorAgent

evaluator = EvidenceEvaluatorAgent()

# Evaluate evidence from experiment
evidence = evaluator.evaluate_evidence(
    experiment=experiment,
    observation="Latency improved to 85ms with cache disabled",
    matches_prediction=True,
    strength=0.8,  # Strong evidence
)

# Update hypothesis belief using Bayes' theorem
updated_belief = evaluator.update_belief(hypothesis, evidence)
print(f"Prior: {hypothesis.belief.prior:.2%}")
print(f"Posterior: {updated_belief.posterior:.2%}")

# Create worktree from schema
worktree_path = evaluator.create_worktree_from_schema(schema)
```

## Agent 3: Backwards Reasoner

**Responsibilities:**
- Calculate inverse conditional probabilities P(Cause|Effect)
- Find conditional variables for reasoning
- Build and query causal graphs
- Suggest hypotheses based on most likely causes

**Key Methods:**

```python
from agents.bayesian import BackwardsReasonerAgent

reasoner = BackwardsReasonerAgent()

# Add variables to causal network
reasoner.add_variable("bug_in_code", description="A bug exists")
reasoner.add_variable("test_failure", description="Tests are failing")
reasoner.add_variable("memory_leak", description="Memory leak present")

# Add causal links with conditional probabilities
reasoner.add_causal_link(
    cause="bug_in_code",
    effect="test_failure",
    strength=0.8,
    conditional_probs={
        ("true", "true"): 0.85,   # P(test_fail|bug) = 0.85
        ("true", "false"): 0.15,
        ("false", "true"): 0.1,   # P(test_fail|no_bug) = 0.1
        ("false", "false"): 0.9,
    }
)

# Calculate backwards probability
prob = reasoner.calculate_backwards_probability(
    cause_var="bug_in_code",
    cause_value="true",
    effect_var="test_failure",
    effect_value="true",
)
print(f"P(bug|test_failure) = {prob:.2%}")

# Query for most likely causes of an effect
query = reasoner.query_causes("test_failure", "true")
print(query.results)  # {"bug_in_code": 0.85, "memory_leak": 0.2, ...}

# Find conditional variables for reasoning
relevant = reasoner.find_conditional_variables(
    target_var="test_failure",
    observed_vars=["recent_change"]
)

# Suggest hypotheses based on backwards reasoning
suggestions = reasoner.suggest_hypotheses_from_effect("test_failure", "true")
```

## Worktree Schema Format

```json
{
  "schema_id": "wts-a1b2c3d4",
  "hypothesis": "Feature X causes performance regression",
  "hypothesis_id": "hyp-x1y2z3",
  "branch_name": "experiment/hyp-x1y2z3-feature-x-causes-perfo",
  "worktree_path": null,
  "prior_probability": 0.6,
  "posterior_probability": null,
  "experiments": [
    {
      "id": "exp-001",
      "description": "Benchmark with Feature X disabled",
      "expected_outcome": "Performance returns to baseline",
      "success_criteria": "p95 < 100ms",
      "status": "designed"
    }
  ],
  "evidence_collected": [],
  "status": "pending",
  "created_at": "2026-01-30T12:00:00Z"
}
```

## Full Workflow Example

```python
from agents.bayesian import BayesianOrchestrator

# Initialize
orchestrator = BayesianOrchestrator()

# Step 1: Set up causal network (Agent 3)
orchestrator.setup_causal_network(
    variables=[
        {"name": "cache_bug", "description": "Bug in caching layer"},
        {"name": "db_slow", "description": "Database queries slow"},
        {"name": "high_latency", "description": "High API latency observed"},
    ],
    causal_links=[
        {"cause": "cache_bug", "effect": "high_latency", "strength": 0.7},
        {"cause": "db_slow", "effect": "high_latency", "strength": 0.8},
    ]
)

# Step 2: Reason from observation (uses all 3 agents)
result = orchestrator.reason_from_observation(
    observation="API latency increased by 50%",
    observation_vars={"high_latency": "true"}
)

# Step 3: Get backwards analysis
print("Most likely causes:", result["backwards_analysis"]["combined_most_likely_causes"])

# Step 4: Hypotheses were auto-generated
for h in result["hypotheses"]:
    print(f"Hypothesis: {h['statement']} (prior: {h['prior']:.2%})")

# Step 5: Run experiments and evaluate results
eval_result = orchestrator.evaluate_experiment_result(
    experiment_id=result["hypotheses"][0]["id"] + "_exp",
    observation="Cache hit ratio dropped to 40%",
    matches_prediction=True,
    strength=0.75,
)

print(f"Posterior: {eval_result['posterior']:.2%}")
print(f"Status: {eval_result['status']}")

# Step 6: Create worktrees for parallel exploration
worktrees = orchestrator.create_all_worktrees()

# Step 7: Export report
orchestrator.export_report()
```

## Bayesian Belief Update

The system uses Bayes' theorem to update beliefs:

```
P(H|E) = P(E|H) * P(H) / P(E)

Where:
- P(H|E) = Posterior probability of hypothesis given evidence
- P(E|H) = Likelihood of evidence if hypothesis is true
- P(H)   = Prior probability of hypothesis
- P(E)   = Marginal probability of evidence
```

**Example update:**

```python
# Prior: 50% chance hypothesis is true
# Evidence strongly supports hypothesis (strength=0.8)

belief = BayesianBelief(prior=0.5)
updated = belief.update(evidence_supports=True, strength=0.8)

# Posterior: ~80% chance hypothesis is true
print(f"Posterior: {updated.posterior:.2%}")
```

## Backwards Reasoning (Abduction)

Agent 3 performs abductive reasoning - inferring causes from effects:

```
Given: Effect E is observed
Find:  Most likely Cause C

P(C|E) = P(E|C) * P(C) / P(E)

Where P(E) = Σ P(E|C_i) * P(C_i) for all possible causes
```

**Example:**

```python
# Observation: Tests are failing
# Question: What caused this?

reasoner.add_causal_link("bug", "test_failure", strength=0.8)
reasoner.add_causal_link("flaky_test", "test_failure", strength=0.3)
reasoner.add_causal_link("env_issue", "test_failure", strength=0.5)

query = reasoner.query_causes("test_failure", "true")

# Results (ranked by probability):
# 1. bug: 0.72
# 2. env_issue: 0.45
# 3. flaky_test: 0.28
```

## Best Practices

- [ ] Start with well-defined causal structures
- [ ] Use informative priors based on domain knowledge
- [ ] Design experiments with clear success criteria
- [ ] Update beliefs incrementally with each piece of evidence
- [ ] Use backwards reasoning to identify non-obvious causes
- [ ] Create worktrees for parallel hypothesis exploration
- [ ] Refine hypotheses when evidence is inconclusive
- [ ] Export reports for documentation and review
