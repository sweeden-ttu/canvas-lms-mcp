# Adaptive Learner Pipeline

Integrated pipeline that fetches Canvas course content, generates a blog series, and produces a Trustworthy AI peer review Reveal.js presentation.

## Overview

The pipeline combines:

1. **Adaptive Course Learner** - Uses `CANVAS_API_TOKEN` (from `.env`) to download course materials via the Canvas API. Perceptron and RL components extract and prioritize content.

2. **Blog Series Generator** - Converts course modules to Jekyll-ready Markdown posts with series navigation and front matter.

3. **Reveal.js Presentation** - Produces a Trustworthy AI peer review deck following the cs-peer-reviewer structure (fairness, privacy, robustness, security, transparency, governance).

## Quick Start

```bash
# Ensure .env has CANVAS_API_TOKEN and CANVAS_BASE_URL
cp .env.example .env
# Edit .env with your token

# Run full pipeline for a course
uv run python orchestrator.py --course-id 58606 --output-dir ./output
```

## Components

| Component | Location | Description |
|-----------|----------|-------------|
| Canvas Fetcher | `adaptive_learner/canvas_fetcher.py` | Fetches modules and items via Canvas API |
| Perceptron | `adaptive_learner/perceptron_model.py` | TF-IDF + MLP importance scoring |
| RL Agent | `adaptive_learner/rl_agent.py` | Q-learning context builder |
| Learner | `adaptive_learner/learner.py` | Orchestrates fetch, learn, persist |
| Blog Generator | `content_pipeline/blog_generator.py` | Course content to Jekyll posts |
| Reveal Generator | `content_pipeline/reveal_generator.py` | Trustworthy AI review deck |

## Output Structure

```
output/
  _posts/                    # Jekyll blog posts (one per module)
  slides/
    trustworthy-ai-peer-review.html
  knowledge_base/
    course_{id}/
      module_{id}/
        items.json
        meta.json
    course_{id}_context.json
    models/
      perceptron.pkl
      rl_agent.json
```

## Software V&V Requirements

See `docs/SOFTWARE_VERIFICATION_VALIDATION_REQUIREMENTS.md` for project proposal verification and validation requirements.

## Tests

```bash
uv run python -m pytest tests/test_adaptive_learner.py tests/test_content_pipeline.py tests/test_orchestrator.py -v
```

## Configuration

Token is loaded from `.env` via `config.py`:

- `CANVAS_API_TOKEN` - Required
- `CANVAS_BASE_URL` - Default: https://texastech.instructure.com
