# Speaker Notes: Trustworthy AI Verification (20 min)

## Timing Guide

| Slide | Topic | Time | Notes |
|-------|-------|------|-------|
| 1 | Title | 0:00 | Intro: 20 min on verification, validation, proofs |
| 2 | Why Verification Matters | 1:00 | Hallucinations, legal/medical harm, RAG/agent risks |
| 3 | V&V Definitions | 2:30 | Proof vs verification vs validation; content verification |
| 4 | What to Verify | 4:00 | Phone, data, news, legal, tests |
| 5 | Legal Luminary Example | 5:30 | Authoritative legal AI; verify every citation |
| 6 | Legal Pipeline | 7:00 | Extract → parse → DB lookup → verify holding |
| 7 | Agent Validators | 8:30 | Validator nodes, input/output/tool validation |
| 8 | Validator Architecture | 10:00 | LangGraph diagram: LLM → Validator → Pass/Fail |
| 9 | Security Reviews | 11:30 | Prompt injection, exfiltration, jailbreaking |
| 10 | Threat Model | 13:00 | Assets, adversaries, attack surfaces |
| 11 | LangChain | 14:30 | Parsers, retrievers, LangSmith |
| 12 | LangGraph Pattern | 16:00 | Code: validator_node, conditional edges |
| 13 | Checklist | 17:30 | Trust = Verification + Transparency + Accountability |
| 14 | Takeaways | 19:00 | Wrap-up |
| 15 | Q&A | 20:00 | Questions |

## Key Points to Emphasize

- **Legal luminary**: An AI that only returns citations verified against LexisNexis/Westlaw. No invented cases.
- **Validator as first-class node**: Not an afterthought; every critical path goes through a validator.
- **Security review**: Red-team your agents. Use GARAK, Vulnhuntr, LLM Canary.
- **LangChain + LangGraph**: Parsers enforce schema; graphs enforce flow; validators enforce trust.

## Running the Slides

Open in browser:
```
open course_content/CS5374-Spring2026/slides/trustworthy-ai-verification.html
```

Or serve locally:
```
cd course_content/CS5374-Spring2026/slides
python -m http.server 8080
# Open http://localhost:8080/trustworthy-ai-verification.html
```

## Demo (Optional)

Install LangGraph if needed:
```
uv add langgraph langchain
```

Run the validator example:
```
uv run python course_content/CS5374-Spring2026/slides/validator_example.py
```
