---
layout: page
title: Project Proposal
permalink: /proposal/
---

## CS5374 Project Proposal – Canvas LMS Adaptive Learning and Content Pipeline

### Summary

This proposal outlines a software verification and validation project integrating Canvas LMS course content with adaptive learning, content generation, and trustworthy AI presentation pipelines. The system aligns with CS5374 topics: testing, LangSmith/LangChain tooling, and AI/LLM verification.

### Scope

| Component | Description |
|-----------|-------------|
| Canvas LMS API | Course content retrieval via MCP server and download_course_content.py |
| Adaptive Course Learner | Perceptron + RL-based context extraction from modules |
| Content Pipeline | Blog series (Jekyll) and Reveal.js presentation generation |
| Validation Pipelines | Content, link, and news validation with LangChain/LangSmith integration |
| Trustworthy AI | Peer review and presentation generation per cs-peer-reviewer skill |

### Verification and Validation Approach

See `docs/SOFTWARE_VERIFICATION_VALIDATION_REQUIREMENTS.md`:

- Unit verification: Config, fetcher, perceptron, RL agent, generators, orchestrator
- Integration verification: Canvas connectivity, fetcher-to-learner, learner-to-blog
- Contract verification: Canvas API schema conformance, well-formed Markdown/HTML

### Deliverables

1. **Proposal** (this document) – Due per syllabus Week 1
2. **Project Plan** – Timeline aligned with 7 course modules
3. **Validation Pipelines** – Content, link, news validators integrated with LangSmith
4. **Jekyll Site** – Proposal and plan (this site)
5. **Skills and Prompts** – Trustworthy AI prompts, LangChain/LangSmith integration
