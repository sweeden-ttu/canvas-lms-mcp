# Building the LaTeX Proposal

## Requirements

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Packages: `fontawesome5`, `tcolorbox`, `tikz`, `hyperref`, `booktabs`, `geometry`, `xcolor`

## Compile

```bash
cd course_content/CS5374-Spring2026
pdflatex proposal_trustworthy_legal_validator.tex
pdflatex proposal_trustworthy_legal_validator.tex   # second run for refs
```

Or with latexmk:

```bash
latexmk -pdf proposal_trustworthy_legal_validator.tex
```

## Output

- `proposal_trustworthy_legal_validator.pdf` - Stylized proposal with diagrams, icons, and clickable links

## Features

- TTU red accent
- FontAwesome5 icons throughout
- TikZ diagrams: validation pipeline, threat model
- Hyperlinks to NewsGuard, PACER, CourtListener, FEC, LangChain, LangGraph, etc.
- Color-coded sections and callout boxes
