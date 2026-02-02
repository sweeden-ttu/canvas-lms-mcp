# CS5374 Project Proposal and Plan

Jekyll static site for the project proposal, project plan, and syllabus alignment.

## Local Development

```bash
cd jekyll_site
bundle install  # or: gem install jekyll
bundle exec jekyll serve
# Open http://localhost:4000
```

## Structure

- `_data/syllabus_modules.yml` – Module topics and timing aligned with Canvas
- `_data/nav.yml` – Navigation
- `proposal.md` – Project proposal (due per syllabus)
- `project-plan.md` – Timeline and deliverables
- `syllabus-alignment.md` – Topics mapped to modules

## GitHub Pages

To deploy: configure Pages to build from `jekyll_site/` or move this directory to repo root and use the default Jekyll workflow.
