"""
Reveal.js Trustworthy AI Peer Review Presentation Generator.

Creates a multi-slide Reveal.js deck for peer reviewing a Trustworthy AI article,
following the cs-peer-reviewer-trustworthy-ai skill structure.
"""

from pathlib import Path


TRUSTWORTHY_AI_DECK_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trustworthy AI Peer Review - {article_title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.0/dist/theme/white.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        .reveal {{ font-size: 1.8rem; }}
        .reveal h2 {{ font-size: 1.6em; border-bottom: 2px solid #333; }}
        .reveal .small {{ font-size: 0.8em; }}
        .callout {{ padding: 1em; border-radius: 8px; margin: 1em 0; }}
        .callout--info {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
        .callout--warn {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
        .callout--success {{ background: #e8f5e9; border-left: 4px solid #4caf50; }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <section>
                <h1>Trustworthy AI Peer Review</h1>
                <h2>{article_title}</h2>
                <p class="small">CS Masters-Level Review</p>
            </section>

            <section>
                <h2>1. Summary</h2>
                <ul>
                    {summary_bullets}
                </ul>
            </section>

            <section>
                <h2>2. Contribution Assessment</h2>
                <ul>
                    <li>What is new?</li>
                    <li>Baseline comparison</li>
                    <li>Practical impact</li>
                </ul>
            </section>

            <section>
                <h2>3. Correctness and Clarity</h2>
                <ul>
                    <li>Ambiguous definitions</li>
                    <li>Missing assumptions</li>
                    <li>Unjustified steps</li>
                    <li>Diagrams vs text alignment</li>
                </ul>
            </section>

            <section>
                <h2>4. Evaluation Rigor</h2>
                <ul>
                    <li>Metrics appropriateness</li>
                    <li>Fair baselines</li>
                    <li>Ablations</li>
                    <li>Reproducibility: datasets, seeds, hyperparameters</li>
                </ul>
            </section>

            <section>
                <h2>5. Trustworthy AI Lens</h2>
                <div class="callout callout--info">
                    <strong>Pillars:</strong> Fairness, Privacy, Robustness, Security, Transparency, Governance
                </div>
                <ul class="small">
                    <li>Fairness: group/individual assumptions, trade-offs</li>
                    <li>Privacy: threat model, mitigations</li>
                    <li>Robustness: distribution shift, adversarial</li>
                    <li>Security: prompt injection, model extraction</li>
                    <li>Transparency: interpretability, model cards</li>
                    <li>Accountability: governance, auditing, monitoring</li>
                </ul>
            </section>

            <section>
                <h2>6. Threat Model</h2>
                <pre class="mermaid">
{threat_model_mermaid}
                </pre>
            </section>

            <section>
                <h2>7. Actionable Recommendations</h2>
                <ul>
                    <li><strong>Must-fix</strong> (blocking)</li>
                    <li><strong>Should-fix</strong> (strongly recommended)</li>
                    <li><strong>Nice-to-have</strong></li>
                </ul>
            </section>

            <section>
                <h2>8. Trustworthy AI Checklist</h2>
                <ul>
                    <li>Fairness considerations addressed</li>
                    <li>Privacy threat model documented</li>
                    <li>Robustness evaluated</li>
                    <li>Security risks identified</li>
                    <li>Transparency and documentation</li>
                    <li>Governance and accountability</li>
                </ul>
            </section>

            <section>
                <h2>Thank you</h2>
                <p>Questions and discussion</p>
            </section>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.0/dist/reveal.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            katex: {{ trust: true }},
            mermaid: {{ startOnLoad: false }}
        }});
        if (typeof mermaid !== 'undefined') mermaid.initialize({{ startOnLoad: false }});
        document.querySelectorAll('pre.mermaid').forEach((el, i) => {{
            mermaid.run({{ nodes: [el], suppressErrors: true }});
        }});
        document.addEventListener('DOMContentLoaded', function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{ left: '$$', right: '$$', display: true }},
                    {{ left: '$', right: '$', display: false }},
                    {{ left: '\\\\[', right: '\\\\]', display: true }},
                    {{ left: '\\\\(', right: '\\\\)', display: false }}
                ]
            }});
        }});
    </script>
</body>
</html>
"""


def generate_trustworthy_ai_review_deck(
    article_title: str,
    summary_bullets: list[str],
    output_path: Path,
    threat_model_mermaid: str | None = None,
) -> Path:
    """
    Generate a Reveal.js deck for Trustworthy AI peer review.

    Args:
        article_title: Title of the article being reviewed
        summary_bullets: List of 3-6 summary bullet points
        output_path: Path to write the HTML file
        threat_model_mermaid: Optional Mermaid diagram for threat model

    Returns:
        Path to generated file
    """
    bullets_html = "\n".join(
        f"<li>{b}</li>" for b in summary_bullets[:6]
    ) or "<li>No summary provided</li>"

    mermaid_default = """graph TD
    A[Data] --> B[Model]
    B --> C[Serving]
    C --> D[User]
    B --> E[Adversary]
    E --> F[Prompt Injection]
    E --> G[Data Poisoning]
    E --> H[Model Extraction]"""

    mermaid = threat_model_mermaid or mermaid_default

    html = TRUSTWORTHY_AI_DECK_TEMPLATE.format(
        article_title=article_title,
        summary_bullets=bullets_html,
        threat_model_mermaid=mermaid,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
