# Software Verification and Validation Requirements

## Summary for Project Proposal

This document summarizes verification and validation (V&V) requirements for the Canvas LMS Adaptive Learning and Content Pipeline system, intended for inclusion in a project proposal or thesis.

---

## 1. Scope

The system integrates:

- **Canvas LMS API** - Course content retrieval via `CANVAS_API_TOKEN`
- **Adaptive Course Learner** - Perceptron + RL-based context extraction
- **Blog Series Generator** - Jekyll-ready output from course modules
- **Trustworthy AI Peer Review** - Reveal.js presentation generator
- **Orchestrator** - End-to-end pipeline coordination

---

## 2. Verification Requirements

### 2.1 Unit Verification

| Component | Requirement | Method |
|-----------|-------------|--------|
| Config loading | `.env` must be present; `CANVAS_API_TOKEN` required | Assert fail on missing; test load_env_config() |
| Canvas fetcher | API calls use correct headers and base URL | Mock httpx; verify Authorization header |
| Perceptron | Feature extraction produces valid vectors | Test extract_features() with fixture content |
| RL agent | Q-table updates follow Q-learning formula | Test update_q_value() with known inputs |
| Blog generator | Output has valid Jekyll front matter | Parse generated YAML; assert required keys |
| Reveal generator | Output is valid HTML with Reveal.js structure | Assert `Reveal.initialize` present |
| Orchestrator | Pipeline stages execute in order | Mock dependencies; assert call sequence |

### 2.2 Integration Verification

| Integration | Requirement | Method |
|-------------|-------------|--------|
| Canvas connectivity | API returns 200 for profile | Live test with real token (optional) |
| Fetcher -> Learner | Course content flows correctly | Integration test with mocked API |
| Learner -> Blog | Context/structure converts to posts | End-to-end test with fixture content |
| Learner -> Reveal | Article metadata flows to deck | Test with sample article |

### 2.3 Contract Verification

- Canvas API responses conform to expected schema (courses, modules, items).
- Generated Markdown/HTML is well-formed and parseable.

---

## 3. Validation Requirements

### 3.1 Functional Validation

- **Correctness**: Extracted course content matches source (module names, item titles).
- **Completeness**: All modules and items are represented in output.
- **Consistency**: Blog series parts link correctly (prev/next).

### 3.2 Non-Functional Validation

| Attribute | Criterion |
|-----------|-----------|
| Performance | Course fetch completes within 60s for typical course |
| Security | Token never logged or emitted in output |
| Usability | Orchestrator CLI provides clear help and error messages |

### 3.3 Trustworthy AI Validation

For the peer review presentation component:

- Fairness, privacy, robustness, security, transparency, and governance are represented.
- Threat model diagram is present and coherent.
- Checklist items are actionable.

---

## 4. Test Strategy

1. **Unit tests**: All core logic (perceptron, RL, generators) with fixtures.
2. **Integration tests**: Orchestrator with mocked Canvas API.
3. **Live tests**: Optional; require `CANVAS_API_TOKEN` in `.env`; skip if unavailable.
4. **Regression tests**: Snapshot or golden-file comparison for generated artifacts.

---

## 5. Acceptance Criteria

- [ ] All unit tests pass without network access.
- [ ] Orchestrator runs end-to-end with mocked Canvas.
- [ ] Generated blog posts render correctly in Jekyll.
- [ ] Generated Reveal.js deck loads in a browser.
- [ ] No hardcoded credentials; `CANVAS_API_TOKEN` from environment only.

---

## 6. References

- IEEE 829 (Software Test Documentation)
- ISO/IEC 25010 (Software product quality)
- Canvas API: https://canvas.instructure.com/doc/api/
