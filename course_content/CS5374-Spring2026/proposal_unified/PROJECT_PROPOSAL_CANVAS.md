# CS5374 Project Proposal (Canvas Submission)

**Course:** Software Verification and Validation | Spring 2026  
**Scope:** Trustworthy AI

---

## Project Title

Trustworthy AI Legal and Governmental Content Validator: Verification of Legal News Sources, Officials, Laws, Court Documents, and Templates

---

## Project Personnel

Scott Weeden, sweeden@ttu.edu (Distance Graduate Student)

---

## Executive Summary (up to 10 lines)

1. LLMs and RAG systems frequently hallucinate legal and governmental content (fake judges, laws, election data), causing serious harm.
2. We build a validation pipeline that verifies content against authoritative sources before AI systems surface it.
3. Content types: legal news, judge names, elected officials, election details and opponents, city/county/state laws, court documents, templates.
4. Method: LangChain and LangGraph validator agents; integration with official registries (courts, election boards, municipal codes); schema validation and source grounding.
5. Trust signal: only verified content returned; all outputs include provenance (source, date, verification status).
6. Hypothesis: verification pipeline significantly reduces hallucination; LangGraph validator nodes outperform post-hoc verification.
7. Experiments: baseline hallucination rate, pipeline effectiveness (precision/recall), validator vs. post-hoc comparison, security red-team (GARAK).
8. Expected: baseline 58–88% hallucination (Stanford); target 95%+ precision post-verification.
9. References: Stanford Law studies, Mata v. Avianca (2023), CourtListener API, GARAK.
10. Aligned with syllabus: V&V, adequacy, black/white box testing, graph-based (LangGraph), security, LangSmith, AI evaluation.

---

## Deliverable (First Round) – 5 lines

1. Design document and threat model for the validation pipeline (prompt injection, data poisoning, source spoofing).
2. Validator modules for legal news sources, judge names, and elected officials; integration with NewsGuard, U.S. Courts, state SOS.
3. LangGraph prototype with validator nodes that route outputs to pass/fail based on verification checks.
4. Unit and integration tests for each validator; documented test coverage for Trustworthy AI criteria.
5. Baseline experiment: measure hallucination rate on legal citation tasks without verification.

---

## Deliverable (Final / Second Round) – 5 lines

1. Full validator suite: legal news, judges, officials, elections, laws, court documents, templates.
2. Integration with authoritative sources per content type (CourtListener, PACER, FEC, eCode360, state legislatures).
3. End-to-end RAG pipeline with validation gates; only verified content retrievable.
4. Security review report (red-team results for prompt injection, exfiltration, tool abuse).
5. 15–20 minute presentation demonstrating the validator pipeline, trust guarantees, and experimental results.

---

*Note: Projects must be defined within the scope of "Trustworthy AI."*
