---
layout: post
title: "Trustworthy AI Legal Validator — Part 3: Content Types and Verification"
date: 2026-01-31
tags: [trustworthy-ai, cs5374, verification]
series: trustworthy-legal-validator
part: 3
description: "Content types and verification strategies."
---

## Content types

| Type | Strategy | Sources |
|------|----------|---------|
| Legal news | Domain trust, fact-check APIs | NewsGuard, AllSides |
| Judge names | Court rosters | U.S. Courts, state courts |
| Elected officials | Gov APIs, election boards | State SOS, Ballotpedia |
| Election details | Certified filings | State boards, FEC |
| Laws | Code repositories | eCode360, legislatures |
| Court documents | PACER, CourtListener | CourtListener API |
| Templates | Form registry, checksum | Official court forms |

## Validation pipeline

```mermaid
flowchart LR
  A[Ingest] --> B[Parse]
  B --> C{Verify}
  C -->|Pass| D[Index]
  C -->|Fail| E[Reject]
```

Only content that passes verification is indexed. All outputs carry provenance (source, date, verification status).
