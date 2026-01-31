# MCP Submodules

This folder holds **git submodules** for MCP (Model Context Protocol) servers. Each submodule is a separate GitHub repository that provides tools to Cursor, Claude, or other MCP clients.

## Adding a new MCP server

From the project root, run:

```bash
./scripts/add_mcp_submodule.sh
# or
uv run python scripts/add_mcp_submodule.py
```

The script will:

1. Prompt for a GitHub source URL (e.g. `https://github.com/user/repo` or `git@github.com:user/repo.git`)
2. Add the repo as a submodule under `mcp/<repo-name>`
3. Clone and sync submodules recursively
4. Register the MCP server in Cursor project settings (`.cursor/mcp.json`)
5. Integrate the server into project documentation and worktrees

## After cloning this repo

If you cloned the main repo without `--recurse-submodules`, initialize and update submodules:

```bash
git submodule update --init --recursive
```

## Listing submodules

```bash
git submodule status
```

## Removing a submodule

```bash
git submodule deinit mcp/<name>
git rm mcp/<name>
rm -rf .git/modules/mcp/<name>
git commit -m "Remove MCP submodule <name>"
```

Then remove its entry from `.cursor/mcp.json` and any docs/worktrees references.
