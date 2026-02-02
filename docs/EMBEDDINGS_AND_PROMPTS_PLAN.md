# Plan: Embeddings and Improved Prompts for Deep-Dive Topics and Expert MCP Integration

This document outlines a plan for generating **embeddings** and **improved prompts** that support (1) deep-dive into topics and (2) expert MCP integration with each new MCP server added under `mcp/`.

---

## Goals

1. **Deep-dive into topics**: Use embeddings to retrieve relevant context (docs, examples, tool descriptions) so the AI can answer with expert-level depth and cite real sources.
2. **Expert MCP integration**: For every new MCP server (added via `./scripts/add_mcp_submodule.sh`), automatically ingest its tools and docs, generate embeddings, and build prompts that enable expert use of that server in the worktree and workflow.
3. **No synthetic data**: All embedded content and prompts must use real documentation, real tool schemas, and real examples (per `.cursor/rules/no-synthetic-data.mdc`). Evidence and reproduction drive updates.

---

## 1. Embeddings Pipeline

### 1.1 What to embed

| Source | Content | Purpose |
|--------|--------|--------|
| **MCP server submodules** (`mcp/<name>/`) | README, tool list/schemas, example snippets, API or CLI docs | Expert use of each MCP server; deep-dive on tools and capabilities |
| **Project docs** | `docs/*.md`, `README.md`, `CLAUDE.md`, `DOCKER.md`, skill/agent descriptions | Project context; Canvas LMS, AutoGen, LangSmith, worktrees |
| **Cursor skills** (`.cursor/skills/*/SKILL.md`) | Skill name, description, usage patterns, code examples | When to use which skill; how to apply them |
| **Cursor agents** (`.cursor/agents/*.md`) | Agent name, description, workflow steps | When to delegate to which agent; presentation-generator, latex-transcriber |
| **Verified specs** | `verified_canvas_spec.json`, endpoint descriptions | Real API shape for Canvas; no mock payloads |
| **Worktrees and rules** | `.cursor/worktrees.json`, `.cursor/rules/*.mdc` | Review-changes, no synthetic data, workflow steps |

Prefer **real** documentation and **real** tool definitions. Do not embed synthetic examples or dummy payloads; if examples are needed, use outputs from live experiments (hypothesis + experiment + evidence) or point to real docs.

### 1.2 Chunking strategy

- **Docs/skills/agents**: Chunk by section (headings) or by fixed token size (e.g. 512–1024 tokens) with overlap. Preserve heading hierarchy so retrieval can return "section + parent section."
- **MCP tools**: One chunk per tool (name + description + input schema + example from docs if present). Optionally one chunk per server (summary + tool list).
- **JSON specs**: Chunk by endpoint or by logical group; keep schema and one real sample per chunk when available.

Store **metadata** per chunk: `source` (file path or server name), `type` (doc | tool | skill | agent | spec), `title` or `tool_name`, `server` (for MCP).

### 1.3 Vector store and retrieval

- **Option A (minimal)**: Embed with a local model or API (e.g. OpenAI embeddings, or sentence-transformers), write vectors to a single file (e.g. `.cursor/embeddings/index.json` or a SQLite DB with a vector extension). Retrieve by cosine similarity or ANN (e.g. faiss, hnswlib).
- **Option B (LangSmith/other)**: Use existing LangSmith or project tracing to store and retrieve runs; attach embeddings to runs for "similar past runs" retrieval.
- **Retrieval**: For each user query or task, retrieve top-k chunks (e.g. k=5–10), optionally filtered by `server` or `type` when the task is MCP-specific. Inject retrieved chunks into the prompt (see Improved prompts).

### 1.4 When to (re)generate embeddings

- **On add MCP submodule**: After cloning a new server under `mcp/<name>`, run an "ingest and embed" step for that server (README, tools, examples). Append to the project index.
- **On project doc/skill/agent change**: Re-embed changed files or re-run full ingestion (e.g. in setup-worktree or a dedicated `scripts/embed_docs.py`).
- **Scheduled or manual**: Optional nightly or pre-release job to refresh embeddings for all sources; or manual `uv run python scripts/embed_docs.py`.

---

## 2. Improved Prompts

### 2.1 System prompt augmentation (RAG)

- **Base context**: Existing project rules (e.g. no synthetic data, review-changes) and high-level docs (README, CLAUDE.md).
- **Retrieved context**: For the current task, retrieve top-k chunks from the embeddings index. Append to system (or user) prompt as "Relevant context:" so the model can deep-dive using real docs and tool definitions.
- **MCP-specific tasks**: When the task mentions a specific MCP server or "use MCP tool X," filter retrieval to that server’s chunks and optionally to `type: tool` so the prompt gets expert-level tool usage.

### 2.2 Expert deep-dive prompts

Templates for "deep-dive" questions that explicitly request use of retrieved context and real sources:

- **Topic deep-dive**: "Using only the project documentation and embedded context, explain [topic]. Cite specific files/sections and do not use synthetic examples."
- **MCP server deep-dive**: "Using the embedded tool docs for `mcp/<name>`, list its tools, describe each tool’s purpose and parameters, and give a step-by-step example using real endpoints/data where possible."
- **Integration deep-dive**: "Using the embedded skills and agents, describe how to combine [skill A] and [agent B] with MCP server [name] for [workflow]. Reference real docs and tool schemas."

Store these as **prompt templates** (e.g. in `.cursor/prompts/` or `docs/`) and wire them to retrieval so that "Relevant context" is filled from the embedding index.

### 2.3 MCP integration prompts (per server)

For each MCP server in `mcp/`:

- **One-shot or few-shot prompt**: "You are an expert user of the [server name] MCP server. Available tools: [list from embedded chunks]. Use these tools for [Canvas content | documentation crawling | presentation enhancement | …]. Prefer real API calls and real data; do not use mock or dummy data."
- **Task-specific prompts**: E.g. "Retrieve course content from Canvas using canvas_* tools, then index it using [new MCP server] tools" — with retrieved tool schemas injected so the model knows exact parameters and return shapes.

Prompts should be **generated or updated** when a new MCP server is added: ingest its tools, embed them, and create a small prompt file or rule (e.g. `.cursor/prompts/mcp-<name>.md`) that references the server and retrieval.

---

## 3. Integration with Each New MCP Server

### 3.1 Extend add-MCP-submodule workflow

After the existing steps (add submodule, sync, install to Cursor, update docs/worktrees), add:

1. **Ingest**: Crawl `mcp/<name>/` for README, package.json or pyproject.toml, tool definitions (e.g. from server code or a manifest). Extract tool name, description, parameters. Use real schemas only.
2. **Embed**: Generate embeddings for each tool and for the README/summary. Append to project embedding index with `server: <name>`, `type: tool` or `doc`.
3. **Prompt template**: Create or update `.cursor/prompts/mcp-<name>.md` (or equivalent) with an expert prompt that references "[Retrieved context for <name>]" and the four evaluation areas (Canvas content, documentation crawling, presentations/orchestration, cross-MCP/schema) from README step 7.
4. **Document**: Add a line to `docs/MCP_SUBMODULES.md` or `docs/EMBEDDINGS_AND_PROMPTS_PLAN.md` that embeddings and prompts were updated for `<name>`; optionally run review-changes to verify no synthetic data was introduced.

### 3.2 Discovery and tool schema extraction

- **Python MCP (FastMCP, etc.)**: Parse `server.py` or entrypoint for `@mcp.tool` or similar; extract name, description, args from docstrings/signatures. Optionally run the server with `--list-tools` or use MCP protocol to list tools and parameters.
- **Node MCP**: Parse package.json scripts and main entry; if the server exposes a tool list (e.g. via CLI or manifest), use that. Otherwise parse source for tool registration and schema.
- **Fallback**: Embed README and any `docs/` in the submodule; prompt template can still say "Use the following context for [server name]" and rely on retrieval at query time.

### 3.3 Expert MCP integration checklist (per server)

For each new server, after embeddings and prompts are generated:

- [ ] Embeddings generated for README and tools (no synthetic payloads).
- [ ] Prompt template created (e.g. `.cursor/prompts/mcp-<name>.md`) and linked to retrieval.
- [ ] Step 7 (evaluate MCP command usefulness) run for Canvas content, docs/examples, presentations/orchestration, cross-MCP/schema.
- [ ] review-changes step run: reproduce ingestion/embed, peer review, accept or reject premise.

---

## 4. Implementation Phases

### Phase 1: Embedding pipeline (project docs and existing MCP)

- Add optional dependency: embedding model or API (e.g. `sentence-transformers`, or `openai` for embeddings).
- Implement `scripts/embed_docs.py`: ingest `docs/`, `.cursor/skills/`, `.cursor/agents/`, README, CLAUDE.md, worktrees.json, rules; chunk; embed; write index to `.cursor/embeddings/` (or similar). Use real content only.
- Document chunk schema and metadata (source, type, title/server).

### Phase 2: Retrieval and prompt injection

- Implement retrieval: load index, take user/task text, embed, return top-k. Optionally filter by type or server.
- Define a small set of **base prompts** (e.g. in `.cursor/prompts/`) that include a placeholder like "{{RELEVANT_CONTEXT}}" and wire them to retrieval in the application or in Cursor rules/instructions.
- Update CLAUDE.md or project instructions to say: "For deep-dives, use the embedding-backed context when available."

### Phase 3: MCP server ingestion and per-server prompts

- Extend `scripts/add_mcp_submodule.py` (or add `scripts/embed_mcp_server.py`) to: ingest new `mcp/<name>/`, extract tool list and descriptions, embed, append to index.
- Auto-generate or update `.cursor/prompts/mcp-<name>.md` with expert prompt text and reference to retrieval for that server.
- Run step 7 (evaluate command usefulness) and review-changes in the plan so that new servers get evaluated and no synthetic data is used.

### Phase 4: Deep-dive and expert templates

- Add **deep-dive** prompt templates (topic, MCP server, integration) under `.cursor/prompts/` or docs, and document when to use them.
- Optionally add a Cursor rule or skill that says: "For MCP expert tasks, use the MCP-specific prompt and retrieved tool context; do not use mock or dummy data."

---

## 5. File and Directory Layout (proposed)

```
.cursor/
  embeddings/           # Optional: vector index and metadata
    index.json          # or SQLite/faiss index
    meta.json           # chunk id -> source, type, server
  prompts/              # Prompt templates
    deep-dive-topic.md
    deep-dive-mcp-server.md
    mcp-<server-name>.md # Per-server expert prompt
docs/
  EMBEDDINGS_AND_PROMPTS_PLAN.md  # This plan
  MCP_SUBMODULES.md
scripts/
  embed_docs.py         # Ingest project docs/skills/agents; chunk; embed; write index
  embed_mcp_server.py   # Ingest one mcp/<name>; embed; append; create prompt template
  add_mcp_submodule.py  # Existing; optionally call embed_mcp_server after add
```

---

## 6. Dependencies and Configuration

- **Embedding model**: Prefer a small local model (e.g. `sentence-transformers`) or a single API (e.g. OpenAI embeddings) to keep the pipeline simple. Document in README or pyproject.toml optional extra `embed`.
- **No synthetic data**: Config and scripts must not embed mock responses, dummy tools, or synthetic examples. If a server has no public tool list, embed only README and document the gap; prompt template can still say "retrieve context for this server when available."
- **review-changes**: Any change to embedding pipeline or prompts must go through the review-changes step (evaluate instructions, peer review, reproduce, accept/reject premise).

---

## 7. Success Criteria

- **Deep-dive**: Users (or the AI) can ask a topic or MCP-server question and get answers backed by retrieved real docs and tool schemas, with citations.
- **Expert MCP integration**: Every new MCP server in `mcp/` gets embeddings and an expert prompt template; step 7 evaluation and review-changes are documented and applied.
- **No synthetic data**: Embeddings and prompts use only real documentation, real tools, and real examples; hypothesis + experiment + evidence used where live data is needed.

This plan can be implemented incrementally (Phase 1 first, then 2–4) and updated as new MCP servers and tools are added.

---

## 8. CI/CD, Docker, VS Code, and Agent Reviews

Concrete automation wired to this plan:

| Area | What |
|------|------|
| **Dockerfile** | Copies `docs/`, `.cursor/`; optional `.[embed]` install; entrypoint `embed` runs `embed_docs.py` then `embed_mcp_server.py` for each `mcp/*/`. |
| **docker-entrypoint.sh** | Case `embed`: `uv run python scripts/embed_docs.py`; loop `mcp/*/` and run `embed_mcp_server.py <name>`. |
| **GitHub Actions** | `.github/workflows/autogen-ci.yml`: job `embeddings` (schedule + manual `run_embeddings`); job `agent-review` (PR + manual `run_agent_review`); workflow_dispatch inputs for both. |
| **GitLab CI** | `.gitlab-ci.yml`: stages `build`, `test`, `embeddings`, `agent-review`; `embeddings` runs on schedule, path changes (docs/.cursor/scripts/mcp), or manual. |
| **VS Code** | `.vscode/tasks.json`: Setup Worktree, Embed Docs, Embed MCP Server, Embed All, Run Tests, Docker Build/Run Server/Run Embed, Agent Review (Checklist). |
| **Agent reviews** | `.cursor/worktrees.json`: `embeddings-pipeline`, `agent-reviews`; `docs/AGENT_REVIEWS.md` checklist for review-changes and embeddings. |
