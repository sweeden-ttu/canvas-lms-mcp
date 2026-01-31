# Reveal.js Plugin Templates and Examples (Trustworthy AI)

Templates and copy-paste examples for each plugin recommended in [REVEAL_PLUGINS_TRUSTWORTHY_AI.md](../REVEAL_PLUGINS_TRUSTWORTHY_AI.md). Use these when building the Trustworthy AI student presentation.

## Layout

| File | Plugin | Purpose |
|------|--------|---------|
| `01-mermaid.html` | reveal.js-mermaid-plugin | Flowcharts, pipelines, governance |
| `02-katex.html` | math-katex / KaTeX-for-reveal | Fairness metrics, DP, formulas |
| `03-chart.html` | Chart (rajgoel) | Bar/line charts, metrics |
| `04-menu.html` | reveal.js-menu | Slide navigation by title |
| `05-toc-progress.html` | TOC-Progress | Section progress bar |
| `06-chalkboard.html` | Chalkboard (rajgoel) | Annotations and drawing |
| `07-code-focus.html` | code-focus | Line-by-line code highlight |
| `08-a11y.html` | a11y | Accessibility |
| `09-poll-questions.html` | Poll / Questions (rajgoel) | Polls and Q&A |
| `10-wordcloud.html` | reveal-wordcloud / tagcloud | Key terms slide |
| `11-pdf-export.html` | PdfExport | PDF handouts |
| `12-title-footer.html` | Title-Footer | Persistent footer title |
| `trustworthy-ai-full.html` | All | Full deck skeleton with all plugins |

## How to use

1. Copy the contents of a snippet file into your Reveal.js deck (inside `<div class="slides">` as a `<section>`).
2. Ensure the plugin is installed and included in your HTML (see REVEAL_PLUGINS_TRUSTWORTHY_AI.md for install steps).
3. For the full deck: use `trustworthy-ai-full.html` as the main HTML file; adjust script/css paths to match your setup (npm or CDN).

## Dependencies

- Reveal.js core (npm: `reveal.js` or CDN)
- Per-plugin: see each snippet file header and REVEAL_PLUGINS_TRUSTWORTHY_AI.md

No synthetic or dummy data; examples use real Trustworthy AI concepts (fairness definitions, DP, bias pipeline).

## MCP submodule addition loop

To add MCP servers as git submodules (e.g. for Cursor integration), run the interactive loop from the repo root:

```bash
./scripts/add_mcp_submodule.sh
# or
uv run python scripts/add_mcp_submodule.py
```

When prompted, enter a GitHub MCP server URL (e.g. `https://github.com/user/repo`). The script adds the submodule under `mcp/<repo-name>`, syncs, updates `.cursor/mcp.json`, and docs/worktrees. Enter `q` to quit the loop.
