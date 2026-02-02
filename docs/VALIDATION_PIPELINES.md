# Validation Pipelines

Content, link, and news validation pipelines for the Canvas LMS MCP project. Integrated with LangChain/LangSmith for tracing and Trustworthy AI prompts.

## Pipelines

| Pipeline | Purpose | Entry Point |
|----------|---------|-------------|
| **Content** | Manifest schema, Jekyll front matter, syllabus structure | `ContentValidationPipeline` |
| **Link** | HTTP(S) URL validation in markdown/HTML | `LinkValidationPipeline` |
| **News** | News/announcement structure, dates, required fields | `NewsValidationPipeline` |

## Usage

### Run All Pipelines

```bash
uv run python pipelines/run_pipelines.py
```

### Run with LangSmith Tracing

Set `LANGCHAIN_API_KEY` and ensure `langsmith` is installed:

```bash
uv run pip install langsmith langchain
export LANGCHAIN_API_KEY=your_key
uv run python -c "
from pipelines.langchain_integration import run_with_tracing
results = run_with_tracing()
print('Content:', len(results['content']), 'checks')
print('Link:', len(results['link']), 'checks')
print('News:', len(results['news']), 'checks')
"
```

### Programmatic Use

```python
from pathlib import Path
from pipelines.content_validator import ContentValidationPipeline
from pipelines.link_validator import LinkValidationPipeline
from pipelines.news_validator import NewsValidationPipeline

root = Path(".")
cv = ContentValidationPipeline(root)
for r in cv.run():
    print(r.name, r.passed, r.message)
```

## Trustworthy AI Integration

- **Prompt**: `.cursor/prompts/trustworthy-ai-validation.md`
- **Skills**: `cs-peer-reviewer-trustworthy-ai` for peer review of generated content
- **LangSmith**: Trace pipeline runs for evaluation and debugging

## Configuration

- **Content**: Validates `course_content/CS5374-Spring2026/manifest.json` and `jekyll_site/**/*.md`
- **Link**: Scans markdown/HTML for URLs; runs HEAD requests
- **News**: Reads `jekyll_site/_data/news.yml` if present, or accepts list of items
