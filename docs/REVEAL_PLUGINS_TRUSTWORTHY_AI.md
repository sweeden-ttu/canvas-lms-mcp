# Reveal.js Plugins for Trustworthy AI Student Presentations

Curated from the [Reveal.js wiki: Plugins, Tools and Hardware](https://github.com/hakimel/reveal.js/wiki/Plugins,-Tools-and-Hardware). These plugins are **installable** (npm or copy) and **add value** for a student presentation on Trustworthy AI (fairness, transparency, accountability, privacy, robustness, security, ethics, bias, explainability).

---

## Recommended plugins (install and add)

### 1. **reveal.js-mermaid-plugin** — Diagrams (flowcharts, state charts)

**Why:** Trustworthy AI slides often need flowcharts (e.g. bias pipeline, fairness metrics flow), state charts (model lifecycle), or simple diagrams. Mermaid renders in-browser; no external server.

- **Install:** `npm install reveal.js-mermaid-plugin`
- **Add:** Include plugin JS and add to `Reveal.initialize({ plugins: [ RevealMermaid ] })`
- **Use for:** Fairness pipeline, data–model–outcome flow, governance process, threat model diagrams.

**Source:** [npm](https://www.npmjs.com/package/reveal.js-mermaid-plugin) | [Mermaid](https://mermaid.js.org/intro/)

---

### 2. **math-katex-plugin** or **KaTeX-for-reveal** — Formulas

**Why:** Trustworthy AI uses formal definitions (fairness metrics, differential privacy epsilon, robustness bounds). KaTeX is fast and lightweight.

- **Install (math-katex-plugin):** [GitHub j13z/reveal.js-math-katex-plugin](https://github.com/j13z/reveal.js-math-katex-plugin) — clone or copy into your plugin folder.
- **Alternative (KaTeX-for-reveal):** [GitHub JeremyHeleine/KaTeX-for-reveal.js](https://github.com/JeremyHeleine/KaTeX-for-reveal.js)
- **Use for:** Equations for demographic parity, equalized odds, DP bounds, loss functions.

---

### 3. **Chart (rajgoel/reveal.js-plugins)** — Charts and graphs

**Why:** Show fairness metrics (bar charts), demographic breakdowns, accuracy–fairness tradeoffs, audit results. Uses Chart.js.

- **Install:** Clone [rajgoel/reveal.js-plugins](https://github.com/rajgoel/reveal.js-plugins), use the `chart` plugin folder; or load Chart.js + plugin script from a CDN/demo.
- **Add:** Include Chart.js, then the plugin JS; register in `Reveal.initialize`.
- **Use for:** Comparison of model performance across groups, confusion matrices, metric dashboards.

**Source:** [reveal.js-plugins/chart](https://github.com/rajgoel/reveal.js-plugins/tree/master/chart) | [Demos](https://rajgoel.github.io/reveal.js-demos)

---

### 4. **reveal.js-menu** — Slide navigation by title

**Why:** Long Trustworthy AI decks (fairness, privacy, robustness, etc.) are easier to navigate with a menu. Students can jump to a section.

- **Install:** Clone or copy from [denehyg/reveal.js-menu](https://github.com/denehyg/reveal.js-menu)
- **Add:** Include plugin JS/CSS; add to `Reveal.initialize({ plugins: [ RevealMenu ] })`
- **Use for:** Quick jump to “Fairness”, “Privacy”, “Robustness”, “Governance”, etc.

**Demo:** [denehyg.github.io/reveal.js-menu](https://denehyg.github.io/reveal.js-menu)

---

### 5. **TOC-Progress** — Beamer-like progress by table of contents

**Why:** Shows progress through major sections (e.g. Intro → Fairness → Privacy → …). Helps audience and presenter keep context.

- **Install:** [e-gor/Reveal.js-TOC-Progress](https://github.com/e-gor/Reveal.js-TOC-Progress)
- **Add:** Include plugin; configure section/slide mapping.
- **Use for:** Section-level progress bar aligned with Trustworthy AI chapters.

**Demo:** [e-gor.github.io/Reveal.js-TOC-Progress/demo](https://e-gor.github.io/Reveal.js-TOC-Progress/demo)

---

### 6. **Chalkboard (rajgoel/reveal.js-plugins)** — Annotations and drawing

**Why:** Live annotations on slides (e.g. circling bias sources, underlining definitions). Good for Q&A and in-class discussion.

- **Install:** From [rajgoel/reveal.js-plugins](https://github.com/rajgoel/reveal.js-plugins), use the `chalkboard` folder.
- **Add:** Include plugin JS/CSS and optional images; register in `Reveal.initialize`.
- **Use for:** Drawing on fairness diagrams, highlighting text, ad-hoc explanations.

**Source:** [chalkboard](https://github.com/rajgoel/reveal.js-plugins/tree/master/chalkboard)

---

### 7. **code-focus** — Highlight specific lines in code blocks

**Why:** Trustworthy AI slides often show code (e.g. fairness constraints, API usage). Focusing line-by-line avoids overwhelming the audience.

- **Install:** [demoneaux/reveal-code-focus](https://github.com/demoneaux/reveal-code-focus)
- **Add:** Include plugin; use `data-line-numbers` or plugin markup for focus.
- **Use for:** Walking through fairness metrics in code, privacy-preserving calls, robustness checks.

**Demo:** [bnjmnt4n.github.io/reveal-code-focus](https://bnjmnt4n.github.io/reveal-code-focus)

---

### 8. **a11y** — Accessibility

**Why:** Accessible presentations (keyboard nav, screen reader support, focus management) align with inclusive design and often with institutional requirements.

- **Install:** [marcysutton/reveal-a11y](https://github.com/marcysutton/reveal-a11y)
- **Add:** Include plugin; optionally configure live region and announcements.
- **Use for:** Accessible navigation and reading order for all students.

---

### 9. **Poll or Questions (rajgoel/reveal.js-plugins)** — Audience interaction

**Why:** Quick polls (“Which fairness definition fits this scenario?”) or Q&A slides increase engagement and check understanding.

- **Install:** From [rajgoel/reveal.js-plugins](https://github.com/rajgoel/reveal.js-plugins): `poll` and/or `questions` (questions builds on `seminar`).
- **Add:** Requires backend/seminar setup for live voting; or use for static Q&A placeholders.
- **Use for:** In-class polls on definitions, ethics dilemmas, or “what would you do?” questions.

**Source:** [poll](https://github.com/rajgoel/reveal.js-plugins/tree/master/poll) | [questions](https://github.com/rajgoel/reveal.js-plugins/tree/master/questions)

---

### 10. **reveal-wordcloud** or **tagcloud-plugin** — Key terms

**Why:** Opening or recap slide with terms (fairness, bias, transparency, accountability, privacy, robustness, security) reinforces vocabulary.

- **Install:** [reveal-wordcloud](https://gitlab.com/andersjohansson/reveal-wordcloud) (wordcloud2.js) or [tagcloud-plugin](https://github.com/sebhildebrandt/reveal.js-tagcloud-plugin)
- **Add:** Include library + plugin; add a slide with wordcloud/tagcloud element.
- **Use for:** “Key concepts” or “Recap” slide for Trustworthy AI.

---

### 11. **PdfExport** — Handouts and PDF

**Why:** Students and instructors often want a PDF version for notes or offline review.

- **Install:** [McShelby/reveal-pdfexport](https://github.com/McShelby/reveal-pdfexport)
- **Add:** Include plugin; use shortcut to toggle PDF export mode.
- **Use for:** Generating handouts for Trustworthy AI deck.

---

### 12. **Title-Footer** — Persistent title

**Why:** Show presentation title (e.g. “Trustworthy AI”) or course/section in a footer so context is always visible.

- **Install:** [e-gor/Reveal.js-Title-Footer](https://github.com/e-gor/Reveal.js-Title-Footer)
- **Add:** Include plugin; set title in config.
- **Demo:** [e-gor.github.io/Reveal.js-Title-Footer/demo](https://e-gor.github.io/Reveal.js-Title-Footer/demo)

---

## Summary table

| Plugin              | Purpose              | Best for Trustworthy AI use           |
|---------------------|----------------------|----------------------------------------|
| reveal.js-mermaid   | Diagrams             | Pipelines, flows, governance           |
| math-katex / KaTeX  | Math                 | Fairness metrics, DP, robustness       |
| Chart (rajgoel)     | Charts               | Metrics, comparisons, audits          |
| reveal.js-menu      | Navigation           | Jump to sections                      |
| TOC-Progress        | Progress             | Section progress bar                   |
| Chalkboard          | Annotations          | Drawing, Q&A                          |
| code-focus          | Code line focus      | Code walkthroughs                      |
| a11y                | Accessibility        | Inclusive presentation                 |
| Poll / Questions    | Interaction          | Polls, Q&A                             |
| reveal-wordcloud    | Key terms            | Vocabulary slide                       |
| PdfExport           | PDF handouts         | Offline / print                        |
| Title-Footer        | Footer title         | Context (e.g. “Trustworthy AI”)        |

---

## Minimal install (npm) example

If using npm with Reveal.js:

```bash
npm install reveal.js reveal.js-mermaid-plugin
# Copy or link other plugins (Chart, Menu, KaTeX, etc.) into a local plugins/ folder
```

In your HTML or entry JS:

```html
<script src="node_modules/reveal.js/dist/reveal.js"></script>
<script src="node_modules/reveal.js-mermaid-plugin/plugin/mermaid/mermaid.js"></script>
<script>
  Reveal.initialize({
    hash: true,
    plugins: [ RevealMermaid ]
  });
</script>
```

---

## Integration with this project

- **presentation-generator** (`.cursor/agents/presentation-generator.md`): When planning or filling Trustworthy AI slides, prefer these plugins for diagrams (Mermaid), math (KaTeX), charts (Chart), navigation (menu), and structure (TOC-Progress, Title-Footer).
- **jekyll-ui-web-designer** (`.cursor/skills/jekyll-ui-web-designer/SKILL.md`): Use this doc when adding Reveal.js plugins to a Jekyll/Reveal layout (e.g. `trustworthy-ai.html`).
- **cs-peer-reviewer-trustworthy-ai**: When producing or reviewing Trustworthy AI lectures, suggest Mermaid/KaTeX/Chart where they improve clarity and rigor; recommend a11y and PdfExport for accessibility and handouts.

All plugin choices use **real** documentation and **real** install paths from the wiki; no synthetic or dummy plugin data.
