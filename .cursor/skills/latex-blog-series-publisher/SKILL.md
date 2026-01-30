---
name: latex-blog-series-publisher
description: Converts a single LaTeX document into a cohesive series of Jekyll-ready blog posts with KaTeX math and Mermaid diagrams. Use when the user mentions LaTeX, lecture notes, turning notes into posts, series generation, KaTeX, Mermaid, or structuring long technical content into multi-part articles.
---

# LaTeX → Blog Series Publisher (Jekyll + KaTeX + Mermaid)

Turn one LaTeX source into a navigable blog series with consistent structure, cross-links, and rendering that works in Jekyll with KaTeX and Mermaid.

## Inputs to request (if missing)

- LaTeX source (`.tex`) and any assets (figures/bib)
- Target site location (Jekyll root) and desired output folder (`_posts/` vs `notes/`)
- Desired series title/slug, and target number of parts (or “auto by sections”)
- Audience level (intro / advanced / mixed)

## Core workflow

1. **Parse the LaTeX outline**
   - Extract `\section`, `\subsection`, `\paragraph` headings.
   - Identify special blocks: equations, code listings, tables, figures, references.

2. **Design the series plan**
   - Map major sections to posts (“Part 1…N”) and keep each post focused.
   - Add a consistent per-post structure:
     - Context + learning goals
     - Main content
     - Worked example
     - Summary + exercises (optional)

3. **Convert content to Markdown suitable for Jekyll**
   - Preserve math delimiters as `\( \)` and `\[ \]` (KaTeX renders these in the browser).
   - Convert LaTeX lists to Markdown lists.
   - Convert `\texttt{}` / `\verb` to backticks.
   - Convert `\begin{verbatim}` / listings to fenced code blocks.

4. **Handle figures/tables**
   - If images are present, reference them under an assets folder (e.g., `assets/img/series-slug/`).
   - If images are not available, insert placeholders:
     - `> TODO: Add figure “...” (from LaTeX Figure X).`

5. **Mermaid extraction**
   - If the LaTeX uses a convention like `\begin{mermaid}...\end{mermaid}` (or commented markers), convert to fenced Mermaid:
     - ```mermaid
       graph TD
       ...
       ```
   - If no Mermaid exists, propose diagrams where it clarifies architecture or workflows.

6. **Create series navigation**
   - Add front matter fields like `series`, `part`, and optional `prev_url`/`next_url`.
   - Add a “Series contents” block at the top of each post linking to all parts.

## Jekyll post template (default)

Use this front matter:
```yaml
---
layout: post
title: "Series Title — Part X: Specific Topic"
date: 2026-01-30
tags: [trustworthy-ai]
series: series-slug
part: 1
description: "One-sentence summary of this part."
---
```

Then structure:
- `## Why this matters`
- `## Key ideas`
- `## Worked example`
- `## Common pitfalls`
- `## Summary`
- `## Exercises` (optional)

## Quality bar

- [ ] No “wall of text”: break up long sections with headings and examples
- [ ] Each post has a clear learning goal and recap
- [ ] Math renders with KaTeX (keep delimiters consistent)
- [ ] Mermaid diagrams render (use fenced blocks)
- [ ] Internal links work, and series ordering is explicit
- [ ] Technical claims have either a derivation, citation, or an example

## What to return to the user

- A complete list of generated Markdown files and where they should live in the Jekyll repo
- Any required site additions (KaTeX/Mermaid includes if not already present)
- A short “edit map” describing which LaTeX sections landed in which post
