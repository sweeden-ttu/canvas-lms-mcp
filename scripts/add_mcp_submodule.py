#!/usr/bin/env python3
"""
Interactive loop: add MCP servers as git submodules under mcp/.

For each GitHub source URL:
1. Add submodule to mcp/<name>
2. Clone and sync submodules recursively
3. Install the MCP server into Cursor project settings (.cursor/mcp.json)
4. Integrate into documentation and worktrees
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_DIR = REPO_ROOT / "mcp"
CURSOR_MCP_JSON = REPO_ROOT / ".cursor" / "mcp.json"
WORKTREES_JSON = REPO_ROOT / ".cursor" / "worktrees.json"
DOCS_MCP = REPO_ROOT / "docs" / "MCP_SUBMODULES.md"


def repo_name_from_url(url: str) -> str:
    """Derive repo name from GitHub URL (user/repo or repo.git -> repo)."""
    url = url.rstrip("/").strip()
    if url.endswith(".git"):
        url = url[:-4]
    parts = url.replace("https://github.com/", "").replace("git@github.com:", "").split("/")
    return parts[-1] if parts else "unknown"


def add_submodule(url: str, path: Path) -> bool:
    """Run git submodule add; return True on success."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "submodule", "add", "--force", url, str(path)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"git submodule add failed: {e.stderr or e}")
        return False


def sync_submodules_recursive() -> bool:
    """Run git submodule update --init --recursive."""
    try:
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"git submodule update failed: {e.stderr or e}")
        return False


def load_cursor_mcp() -> dict:
    """Load .cursor/mcp.json; return dict with mcpServers key."""
    if CURSOR_MCP_JSON.exists():
        data = json.loads(CURSOR_MCP_JSON.read_text())
        return data if isinstance(data, dict) else {"mcpServers": {}}
    return {"mcpServers": {}}


def ensure_mcp_servers_key(data: dict) -> dict:
    if "mcpServers" not in data:
        data["mcpServers"] = {}
    return data


def infer_server_command(submodule_path: Path) -> dict:
    """Infer command/args for an MCP server (Python uv run server.py or npx)."""
    resolved = str(submodule_path.resolve())
    # Prefer uv + server.py (Python MCP)
    server_py = submodule_path / "server.py"
    if server_py.exists():
        return {
            "command": "uv",
            "args": ["--directory", resolved, "run", "python", "server.py"],
        }
    # Node: package.json with scripts.start or main (use npx from submodule dir)
    package_json = submodule_path / "package.json"
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text())
            scripts = pkg.get("scripts") or {}
            if "start" in scripts:
                return {"command": "sh", "args": ["-c", f"cd {resolved} && npm run start"]}
            main = pkg.get("main", "dist/index.js")
            return {"command": "sh", "args": ["-c", f"cd {resolved} && node {main}"]}
        except (json.JSONDecodeError, OSError):
            pass
    # Fallback: uv run python server.py (user can edit .cursor/mcp.json)
    return {"command": "uv", "args": ["--directory", resolved, "run", "python", "server.py"]}


def install_to_cursor(name: str, submodule_path: Path) -> None:
    """Add or update MCP server entry in .cursor/mcp.json."""
    CURSOR_MCP_JSON.parent.mkdir(parents=True, exist_ok=True)
    data = load_cursor_mcp()
    ensure_mcp_servers_key(data)
    entry = infer_server_command(submodule_path)
    data["mcpServers"][name] = entry
    CURSOR_MCP_JSON.write_text(json.dumps(data, indent=2))
    print(f"  Updated {CURSOR_MCP_JSON}")


def integrate_docs(name: str, url: str, _submodule_path: Path) -> None:
    """Append or update docs/MCP_SUBMODULES.md."""
    DOCS_MCP.parent.mkdir(parents=True, exist_ok=True)
    entry = f"- **{name}** (`mcp/{name}`): {url}\n"
    header = "# MCP Submodules\n\nMCP servers added as git submodules under `mcp/`.\n\n## Registered servers\n\n"
    if DOCS_MCP.exists():
        content = DOCS_MCP.read_text()
        if f"mcp/{name}" in content:
            print(f"  Updated {DOCS_MCP} (entry exists)")
            return
        if "## Registered servers" in content:
            # Insert after first list block or at end of section
            idx = content.find("\n- **", content.find("## Registered servers"))
            if idx != -1:
                content = content[:idx] + entry + content[idx:]
            else:
                content = content.rstrip() + "\n" + entry + "\n"
        else:
            content = content.rstrip() + "\n\n" + entry
        DOCS_MCP.write_text(content)
    else:
        DOCS_MCP.write_text(header + entry)
    print(f"  Updated {DOCS_MCP}")


def integrate_worktrees(name: str) -> None:
    """Add MCP server to .cursor/worktrees.json mcp list if present."""
    if not WORKTREES_JSON.exists():
        return
    data = json.loads(WORKTREES_JSON.read_text())
    if "mcpSubmodules" not in data:
        data["mcpSubmodules"] = []
    if name not in data["mcpSubmodules"]:
        data["mcpSubmodules"].append(name)
        WORKTREES_JSON.write_text(json.dumps(data, indent=2))
        print(f"  Updated {WORKTREES_JSON}")


def one_round() -> bool:
    """Prompt for URL, add submodule, sync, install to Cursor, integrate. Return False to exit."""
    url = input("\nGitHub MCP server URL (or 'q' to quit): ").strip()
    if not url or url.lower() == "q":
        return False
    name = repo_name_from_url(url)
    path = MCP_DIR / name
    if path.exists():
        print(f"  Path mcp/{name} already exists. Syncing recursively.")
        sync_submodules_recursive()
        install_to_cursor(name, path)
        integrate_docs(name, url, path)
        integrate_worktrees(name)
        return True
    print(f"  Adding submodule mcp/{name} ...")
    if not add_submodule(url, path):
        return True
    if not sync_submodules_recursive():
        return True
    install_to_cursor(name, path)
    integrate_docs(name, url, path)
    integrate_worktrees(name)
    print(f"  Done. Restart Cursor or reload MCP settings to use '{name}'.")
    return True


def main() -> int:
    MCP_DIR.mkdir(parents=True, exist_ok=True)
    print("MCP submodule manager. Enter a GitHub repo URL to add it under mcp/.")
    print("Each addition: submodule add -> sync recursive -> Cursor mcp.json -> docs & worktrees.")
    while one_round():
        pass
    print("Bye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
