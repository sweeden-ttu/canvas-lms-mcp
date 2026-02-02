---
name: jekyll-ui-web-designer
description: Designs and implements functional UI layouts for Jekyll/static sites. Use when the user requests Jekyll pages, layouts, navigation, theming, responsive components, GitHub Pages sites, KaTeX math rendering, Mermaid diagrams, or Reveal.js slide pages.
---

# Jekyll UI & Web Designer (KaTeX + Mermaid + Reveal.js)

Create clean, functional layouts and content structures for Jekyll and other static page builders, with first-class support for KaTeX, Mermaid, and slide decks.

## Quick Start (default deliverables)

When asked to “build a layout” or “make a site,” produce:
- `_layouts/` with `default.html`, `page.html`, `post.html`, `slides.html`
- `_includes/` with `head.html`, `header.html`, `footer.html`
- `_data/nav.yml` for navigation
- `assets/` for CSS/JS, including Mermaid + KaTeX init
- `index.md` and at least one example page/post
- `slides/` with at least one Reveal.js deck page

## Assumptions (unless user overrides)

- Use **Jekyll** with a **minimal, dependency-light** approach (CDN-based KaTeX/Mermaid/Reveal).
- Use **KaTeX** for math; keep math in source as `\( \)` and `\[ \]` so it renders in both posts and slides.
- Use **client-side Mermaid**: fenced code blocks with ```mermaid.

## Site Structure Blueprint

Recommended structure:
```
.
├── _config.yml
├── _data/
│   └── nav.yml
├── _includes/
│   ├── head.html
│   ├── header.html
│   └── footer.html
├── _layouts/
│   ├── default.html
│   ├── page.html
│   ├── post.html
│   └── slides.html
├── _posts/
│   └── YYYY-MM-DD-title.md
├── assets/
│   ├── css/site.css
│   └── js/
│       ├── mermaid-init.js
│       └── katex-init.js
├── slides/
│   └── trustworthy-ai.html
└── index.md
```

## Layout Implementation Guidelines

### Core layout behavior
- Keep a single `default` layout that defines the page chrome (header/nav/footer).
- Use semantic HTML (`main`, `nav`, `header`, `footer`) and accessible patterns.
- Use responsive CSS with a readable baseline:
  - max content width (e.g., 70–80ch)
  - comfortable line-height
  - good contrast

### Navigation
Drive nav from `_data/nav.yml`, e.g.:
```yml
- title: Home
  url: /
- title: Blog
  url: /blog/
- title: Slides
  url: /slides/
```

### KaTeX
- Include KaTeX CSS/JS in `_includes/head.html` (CDN).
- Add `assets/js/katex-init.js` that renders math in the document body.
- Keep authoring format in Markdown/HTML as `\( ... \)` and `\[ ... \]`.

### Mermaid
- Include Mermaid (CDN) in `_includes/head.html` (or just before `</body>`).
- Initialize Mermaid in `assets/js/mermaid-init.js` against `pre > code.language-mermaid` blocks.

### Reveal.js slides
Prefer a standalone `slides/*.html` deck using Reveal.js via CDN so it works anywhere (no build tooling required).
- Include KaTeX and Mermaid on slides pages too.
- Use vertical slides for “multi-page depth” within one deck (Reveal sections inside sections).

## Content Conventions (front matter)

### Pages
```yaml
---
layout: page
title: "About"
permalink: /about/
---
```

### Posts
```yaml
---
layout: post
title: "Post Title"
date: 2026-01-30
tags: [trustworthy-ai, notes]
series: trustworthy-ai
part: 1
---
```

### Slides index page (optional)
Create a `slides/index.md` that lists decks and links to `slides/*.html`.

## Component Patterns (portable)

When the user asks for “components,” implement as:
- Include partials in `_includes/` for reusable UI (hero, callout, card grid)
- Use simple, class-based CSS in `assets/css/site.css`

**Common components:**
- Callout: `.callout.callout--info|--warn|--success`
- Two-column layout: `.grid.grid--2`
- Cards: `.cards > .card`

## Output Checklist (quality bar)

- [ ] Builds without custom plugins (unless user explicitly wants them)
- [ ] Responsive across mobile/desktop
- [ ] Accessible nav and headings (no skipped levels)
- [ ] KaTeX renders inline and display math
- [ ] Mermaid diagrams render (and degrade gracefully if JS blocked)
- [ ] Reveal.js deck loads and can be navigated with keyboard

## What to return to the user

Return:
- The file tree you created/modified
- Any required config additions (e.g., `_config.yml` settings)
- A short “how to preview” note (e.g., `bundle exec jekyll serve` if bundler is used; otherwise whatever the repo already uses)
