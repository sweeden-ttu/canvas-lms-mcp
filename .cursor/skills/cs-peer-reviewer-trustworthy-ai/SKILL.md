---
name: cs-peer-reviewer-trustworthy-ai
description: Performs CS Masters–level peer reviews and produces in-depth Trustworthy AI presentations with real-world examples. Use when reviewing academic drafts, research ideas, project reports, or when creating multi-slide Reveal.js lectures on Trustworthy AI (fairness, privacy, robustness, security, transparency, governance).
---

# CS Peer Reviewer + Trustworthy AI Presentation Builder

Provide rigorous, constructive peer review for Computer Science Masters–level work and produce multi-slide Reveal.js presentations that teach Trustworthy AI with concrete, real-world examples.

## Inputs to request (if missing)

- The artifact to review (paper/draft/proposal/slides/code) and its goal
- Intended venue or rubric (course, thesis proposal, workshop paper)
- Audience level and time budget (e.g., 15/30/60 minutes)
- Any constraints (must use Reveal.js, must include Mermaid/KaTeX, etc.)

## Peer review workflow (Masters level)

1. **Summarize first**
   - 3–6 bullets capturing: problem, method, evaluation, key results/claims.

2. **Assess contribution**
   - What is new? What is the baseline? What is the practical impact?

3. **Correctness and clarity**
   - Identify ambiguous definitions, missing assumptions, or unjustified steps.
   - Flag diagrams/figures that don’t match the text.

4. **Evaluation rigor**
   - Are metrics appropriate? Baselines fair? Ablations present?
   - Reproducibility: datasets, seeds, hyperparameters, compute budget.

5. **Trustworthy AI lens**
   - Fairness: group/individual fairness assumptions and trade-offs.
   - Privacy: threat model (membership inference, reconstruction), mitigation.
   - Robustness: distribution shift, adversarial robustness, calibration.
   - Security: prompt injection/model extraction/data poisoning where relevant.
   - Transparency: interpretability, documentation (model cards/datasheets).
   - Accountability: governance, auditing, monitoring, incident response.

6. **Actionable recommendations**
   - Provide a prioritized fix list:
     - Must-fix (blocking)
     - Should-fix (strongly recommended)
     - Nice-to-have

## Review output format (default)

Return feedback as:
- **Summary**
- **Strengths**
- **Weaknesses / Risks**
- **Questions for the author**
- **Concrete improvements (prioritized)**
- **Suggested experiments / ablations**
- **Trustworthy AI checklist results**

## Presentation workflow (Reveal.js deep dive)

### Default deck characteristics
- Reveal.js deck (single HTML page) with:
  - KaTeX support for `\( \)` and `\[ \]`
  - Mermaid support for fenced ` ```mermaid ` diagrams
  - Speaker notes for “in depth” explanations

### Suggested deck structure (Trustworthy AI)

1. Motivation + real incidents (2–3 slides)
2. Definitions and scope (what “trustworthy” means in context)
3. Threat models (what can go wrong and who the adversary is)
4. Core pillars (fairness, privacy, robustness, security, transparency, governance)
5. Measurement and evaluation pitfalls (metrics, proxies, distribution shift)
6. Engineering practices (testing, monitoring, red-teaming, documentation)
7. Case study walkthrough (end-to-end)
8. Checklist + takeaways

### Real-world example patterns (include at least one)
- **Fairness**: disparate impact from label bias; mitigation with reweighing + post-processing.
- **Privacy**: membership inference risk; mitigation with DP-SGD trade-offs.
- **Robustness**: distribution shift in deployment; monitoring + retraining triggers.
- **Security**: prompt injection / data exfiltration in LLM apps; sandboxing + allowlists.

## Mermaid diagrams to use often

- System context diagram (data → model → serving → user)
- Threat model diagram (actors, assets, attack surfaces)
- MLOps lifecycle (train → eval → deploy → monitor → incident response)

## What to return to the user

Depending on the ask:
- A peer review in the default format above
- A slide outline, then a complete Reveal.js deck file (HTML) with speaker notes
- Concrete “next steps” the student can execute in a week (experiments, rewrites, readings)
