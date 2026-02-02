# Trustworthy AI container (Podman)

Container image based on [gitlab.com/sweeden3/trustworthy-ai](https://gitlab.com/sweeden3/trustworthy-ai). Built and run with Podman from inside the canvas-lms-mcp repository.

## Build

From the **canvas-lms-mcp** repo root:

```bash
podman build -f containers/trustworthy-ai/Containerfile -t trustworthy-ai:latest .
```

Optional build args (branch; for private repo use a URL with token in a build-arg):

```bash
podman build -f containers/trustworthy-ai/Containerfile \
  --build-arg REPO_BRANCH=main \
  -t trustworthy-ai:latest .
```

## Run

```bash
podman run -d --name trustworthy-ai -p 8080:80 trustworthy-ai:latest
```

Then open http://localhost:8080 .

## One-liner (build + run)

From canvas-lms-mcp root:

```bash
./scripts/run_trustworthy_ai_podman.sh
```

Or:

```bash
podman build -f containers/trustworthy-ai/Containerfile -t trustworthy-ai:latest . && \
podman run -d --name trustworthy-ai -p 8080:80 trustworthy-ai:latest
```

## Stop and remove

```bash
podman stop trustworthy-ai
podman rm trustworthy-ai
```
