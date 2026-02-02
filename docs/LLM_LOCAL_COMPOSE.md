# Run LLMs Locally with Compose / Podman

This setup provides a **local LLM runner** via Docker Compose (or Podman Compose), similar in spirit to [Docker Model Runner](https://www.docker.com/blog/run-llms-locally/) but using standard images and compose. The layout is inspired by the [GitLab Runner Kubernetes agent](https://docs.gitlab.com/runner/install/kubernetes-agent/) pattern: one service, config via env, persistent volume.

## Default: Ollama

- **Image:** `ollama/ollama` ([Ollama Docker](https://docs.ollama.com/docker))
- **Port:** 11434 (OpenAI-compatible API)
- **Volume:** `llm-data` for model storage

## Files

| File | Purpose |
|------|--------|
| `docker-compose.llm.yml` | Compose stack for the LLM runner service |
| `.env.llm.example` | Example env; copy to `.env.llm` and set `LLM_IMAGE`, `LLM_COMMAND`, `LLM_PORT` if you use a custom image/command |

## Run with Docker Compose

```bash
docker compose -f docker-compose.llm.yml --env-file .env.llm up -d
# Pull a model (inside container or host if Ollama CLI installed):
# docker exec -it llm-runner ollama run llama3.2
```

## Run with Podman Compose

```bash
podman-compose -f docker-compose.llm.yml --env-file .env.llm up -d
# Or with podman only: see below.
```

## Custom image and command

1. Copy `.env.llm.example` to `.env.llm`.
2. Set `LLM_IMAGE` to your image (e.g. a custom Ollama-based or other OpenAI-compatible server).
3. Optionally set `LLM_COMMAND` to the entrypoint/command.
4. Run compose as above; the stack will use your image and command.

## Verify with Podman

From the repo root (or the directory containing `docker-compose.llm.yml`):

```bash
podman-compose -f docker-compose.llm.yml up -d
podman ps
curl -s http://localhost:11434/api/tags
```

Or with plain Podman (one container, no compose):

```bash
podman run -d -v llm-data:/root/.ollama -p 11434:11434 --name llm-runner ollama/ollama
podman ps
```

After you create your image and command, run the same from the location you use and confirm the container is up and the API responds.
