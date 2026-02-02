# Unified Project Proposal Package

Single submission package for the Trustworthy AI Legal and Governmental Content Validator project (CS5374 Spring 2026).

## Contents

| Item | Path | Description |
|------|------|-------------|
| **Full Proposal** | `PROJECT_PROPOSAL.md` | Complete proposal with hypothesis, experiments, expected results, references |
| **LaTeX (PDF)** | `proposal_unified.tex` | Condensed LaTeX for PDF submission; build with `pdflatex` |
| **Jekyll Blog** | `jekyll/` | Blog series (4 parts) with proposal content |
| **Presentation** | `../slides/trustworthy-ai-verification.html` | 20-min Reveal.js deck, syllabus-aligned |

## Proposal Sections

- Introduction and Summary (prose)
- Hypothesis
- Experiments (4: baseline, pipeline effectiveness, architecture comparison, security)
- Expected Experimental Results
- Syllabus Alignment (weeks 1-2, 4-9, 10, 16-17)
- Deliverables (first and final round)
- Content Types and Verification Strategies
- References (Stanford Law, Mata v. Avianca, CourtListener, GARAK, etc.)

## Build

**LaTeX:**
```bash
cd proposal_unified
pdflatex proposal_unified.tex
```

**Jekyll:**
```bash
cd proposal_unified/jekyll
bundle exec jekyll serve
# or: jekyll serve (if Jekyll installed)
```

**Presentation:**
Open `../slides/trustworthy-ai-verification.html` in a browser.

## Submission

For Canvas: submit `PROJECT_PROPOSAL.md` or the PDF built from `proposal_unified.tex`. The blog and presentation support the proposal for mid-semester and final presentations.
