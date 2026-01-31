# Self-hosted GitHub Runner with Podman (CI/CD reproduce step)

The AutoGen CI/CD pipeline includes a **reproduce-failure** job that runs only when the **build-test** job fails. That job:

1. Reviews errors by re-running the same steps (ruff, mypy, pytest) inside a Podman container.
2. Builds one Podman image from `.github/reproduce/Dockerfile.repro`.
3. Runs **one Podman pod** on the runner host (single container) to reproduce the failing run.
4. Writes `repro.log` and extracts error lines to `repro-errors.txt`, then uploads them as workflow artifacts.

The job uses a **self-hosted runner** so that Podman is available and so only one pod is created per CI/CD job on that host.

---

## Create the GitHub runner (self-hosted with Podman)

Run these steps on a machine that will act as the self-hosted runner (e.g. a Linux server or VM with Podman installed).

### 1. Install Podman

On Fedora / RHEL:

```bash
sudo dnf install -y podman
```

On Ubuntu 22.04:

```bash
sudo apt-get update && sudo apt-get install -y podman
```

Verify:

```bash
podman --version
```

### 2. Add the self-hosted runner to the repository

1. In GitHub: open the repo **Settings** → **Actions** → **Runners**.
2. Click **New self-hosted runner**.
3. Choose **Linux** (or your OS) and the architecture (e.g. x64).
4. Follow the commands shown by GitHub. They look like:

```bash
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf actions-runner-linux-x64-2.311.0.tar.gz
./config.sh --url https://github.com/OWNER/REPO --token RUNNER_TOKEN
```

5. When prompted for **labels**, add (in addition to the default `self-hosted` and `Linux`):

   - **podman**

   So the job `runs-on: [self-hosted, podman]` will run only on this runner.

   Example:

   ```bash
   ./config.sh --url https://github.com/OWNER/REPO --token RUNNER_TOKEN --labels self-hosted,Linux,X64,podman
   ```

6. Install and start the runner (as a service, optional):

```bash
./svc.sh install
./svc.sh start
```

Or run it in the foreground for testing:

```bash
./run.sh
```

### 3. One pod per CI/CD job

The workflow runs **one** Podman pod per **reproduce-failure** job. The script `.github/reproduce/run-repro.sh` creates a single pod, runs one container in it, then removes the pod. If you run multiple jobs on the same runner, each job gets its own pod (created and torn down for that job).

---

## When the reproduce job runs

- **Trigger:** Only when **build-test** fails (`if: failure() && needs.build-test.result == 'failure'`).
- **Runner:** Must have label `podman` (and usually `self-hosted`, `Linux`).
- **Artifacts:** `podman-repro-log-<run_id>` containing `repro.log` and `repro-errors.txt` (retention 14 days).

If no self-hosted runner with label `podman` is available, the **reproduce-failure** job will remain queued until such a runner is added.

---

## Local reproduction (without CI)

From the repo root, with Podman installed:

```bash
chmod +x .github/reproduce/run-repro.sh
.github/reproduce/run-repro.sh .
```

Optional env vars: `CANVAS_API_TOKEN`, `CANVAS_BASE_URL`, `IMAGE_NAME`, `POD_NAME`, `LOG_FILE`, `ERRORS_FILE`.
