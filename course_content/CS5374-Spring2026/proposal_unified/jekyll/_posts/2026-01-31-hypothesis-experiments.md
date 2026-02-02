---
layout: post
title: "Trustworthy AI Legal Validator — Part 2: Hypothesis and Experiments"
date: 2026-01-31
tags: [trustworthy-ai, cs5374, experiments]
series: trustworthy-legal-validator
part: 2
description: "Hypothesis, experiments, and expected results."
---

## Hypothesis

We hypothesize that (1) a pipeline verifying content against authoritative databases will significantly reduce hallucination rates in legal citations, and (2) LangGraph validator nodes (with pass/fail routing) will outperform post-hoc verification by enabling retries before outputs are surfaced.

## Experiments

**Experiment 1 – Baseline:** Establish hallucination rate for an LLM on legal citation tasks without verification.

**Experiment 2 – Pipeline effectiveness:** Implement validator using CourtListener API. Measure precision, recall, hallucination rate.

**Experiment 3 – Architecture comparison:** Compare LangGraph validator nodes vs. post-hoc verification (accuracy, latency).

**Experiment 4 – Security:** Apply GARAK for prompt injection, exfiltration, source spoofing.

## Expected results

- Baseline: 58–88% hallucination (consistent with Stanford)
- Target: 95%+ precision post-verification
- Red-team: Document 1–2 injection vectors and mitigations
