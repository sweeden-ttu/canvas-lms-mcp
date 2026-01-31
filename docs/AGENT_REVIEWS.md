# Agent Reviews (review-changes step)

This document defines the **agent review** checklist used after change sets (PRs, merge requests, or delivered tasks). It aligns with `.cursor/rules/no-synthetic-data.mdc` and `.cursor/worktrees.json` `review-changes`.

## When to run

- After any change set (PR, commit batch, or delivered task).
- Before merging or finalizing changes.
- In CI: GitHub Actions `agent-review` job; GitLab CI `agent-review` stage; VS Code task **Agent Review (Checklist)**.

## Checklist

1. **Evaluate step-by-step instructions**  
   Review the instructions that were followed. Confirm they do not rely on synthetic, mock, or dummy data.

2. **Peer review**  
   Apply peer review using:
   - **cs-peer-reviewer-trustworthy-ai** (Trustworthy AI / CS Masters-level review).
   - **evidence_evaluator** (EvidenceEvaluatorAgent).
   - **BayesianOrchestrator** where hypothesis/evidence updates are relevant.

3. **Reproduce**  
   Run the same steps in a clean environment and verify outcomes:
   - Re-run tests: `uv run pytest tests/ -v --tb=short`
   - Re-fetch data (e.g. live Canvas API if applicable).
   - Re-build (e.g. `docker build -t canvas-lms-mcp:latest .`).

4. **Accept or reject premise**  
   - **Accept**: If reproduction succeeds and no synthetic/mock/dummy data was introduced, accept the premise and keep the change.  
   - **Reject**: If mock/synthetic/dummy data would have been used or results cannot be reproduced, reject the premise and revert or rewrite so that real data and reproducible evidence are used.

## Embeddings and prompts

For changes to the **embeddings pipeline** or **prompts** (see `docs/EMBEDDINGS_AND_PROMPTS_PLAN.md`):

- Run **Embed Docs** (and **Embed MCP Server** for each new MCP submodule) and confirm index/prompts are updated.
- Confirm no synthetic payloads or dummy examples are embedded; use real docs and real tool schemas only.
- Run the full checklist above and document that review-changes was completed.

## CI integration

- **GitHub**: `.github/workflows/autogen-ci.yml` — `embeddings` job and `agent-review` job.
- **GitLab**: `.gitlab-ci.yml` — `embeddings` and `agent-review` stages.
- **VS Code**: Run task **Agent Review (Checklist)** from the Command Palette (`Tasks: Run Task`).
