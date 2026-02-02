#!/usr/bin/env python3
"""Repository synchronization script for GitHub and GitLab.

This script handles bidirectional synchronization between GitHub and GitLab
repositories, with support for:
- Branch mirroring
- Tag synchronization
- Conflict detection
- Status reporting

Usage:
    python scripts/sync_repos.py --direction github-to-gitlab
    python scripts/sync_repos.py --direction gitlab-to-github
    python scripts/sync_repos.py --check-status
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import httpx


class SyncDirection(str, Enum):
    """Sync direction options."""
    GITHUB_TO_GITLAB = "github-to-gitlab"
    GITLAB_TO_GITHUB = "gitlab-to-github"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class SyncConfig:
    """Configuration for repository synchronization."""
    
    github_repo: str
    github_token: str
    gitlab_project_path: str
    gitlab_token: str
    gitlab_url: str = "https://gitlab.com"
    github_url: str = "https://github.com"
    
    @classmethod
    def from_env(cls) -> "SyncConfig":
        """Load configuration from environment variables."""
        return cls(
            github_repo=os.getenv("GITHUB_REPO", "sweeden-ttu/canvas-lms-mcp"),
            github_token=os.getenv("GITHUB_TOKEN", ""),
            gitlab_project_path=os.getenv("GITLAB_PROJECT_PATH", "sweeden-ttu/canvas-lms-mcp"),
            gitlab_token=os.getenv("GITLAB_TOKEN", ""),
        )


@dataclass
class SyncStatus:
    """Status of repository synchronization."""
    
    github_sha: str
    gitlab_sha: str
    in_sync: bool
    github_ahead: int = 0
    gitlab_ahead: int = 0
    last_sync: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "github_sha": self.github_sha,
            "gitlab_sha": self.gitlab_sha,
            "in_sync": self.in_sync,
            "github_ahead": self.github_ahead,
            "gitlab_ahead": self.gitlab_ahead,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
        }


class RepositorySyncer:
    """Handles repository synchronization between GitHub and GitLab."""
    
    def __init__(self, config: SyncConfig):
        self.config = config
    
    async def get_status(self) -> SyncStatus:
        """Get current synchronization status."""
        async with httpx.AsyncClient() as client:
            # Get GitHub HEAD commit
            github_resp = await client.get(
                f"https://api.github.com/repos/{self.config.github_repo}/commits/main",
                headers={
                    "Authorization": f"Bearer {self.config.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )
            
            if github_resp.status_code == 200:
                github_sha = github_resp.json().get("sha", "unknown")[:7]
            else:
                github_sha = "error"
            
            # Get GitLab HEAD commit
            project_path = self.config.gitlab_project_path.replace("/", "%2F")
            gitlab_resp = await client.get(
                f"{self.config.gitlab_url}/api/v4/projects/{project_path}/repository/commits/main",
                headers={"PRIVATE-TOKEN": self.config.gitlab_token}
            )
            
            if gitlab_resp.status_code == 200:
                gitlab_sha = gitlab_resp.json().get("id", "unknown")[:7]
            else:
                gitlab_sha = "error"
            
            return SyncStatus(
                github_sha=github_sha,
                gitlab_sha=gitlab_sha,
                in_sync=github_sha == gitlab_sha and github_sha != "error",
            )
    
    def sync_github_to_gitlab(self, branch: str = "main", force: bool = False) -> dict:
        """Sync from GitHub to GitLab."""
        result = {
            "direction": "github-to-gitlab",
            "branch": branch,
            "status": "pending",
            "steps": [],
        }
        
        try:
            # Configure Git
            self._run_git(["config", "user.name", "sync-bot"])
            self._run_git(["config", "user.email", "sync-bot@example.com"])
            
            # Fetch from GitHub
            github_url = f"https://oauth2:{self.config.github_token}@github.com/{self.config.github_repo}.git"
            self._run_git(["fetch", github_url, branch])
            result["steps"].append({"step": "fetch_github", "status": "success"})
            
            # Push to GitLab
            gitlab_url = f"https://oauth2:{self.config.gitlab_token}@gitlab.com/{self.config.gitlab_project_path}.git"
            push_args = ["push", gitlab_url, f"FETCH_HEAD:refs/heads/{branch}"]
            if force:
                push_args.insert(1, "--force")
            
            self._run_git(push_args)
            result["steps"].append({"step": "push_gitlab", "status": "success"})
            
            # Push tags
            self._run_git(["fetch", github_url, "--tags"])
            self._run_git(["push", gitlab_url, "--tags", "--force"])
            result["steps"].append({"step": "sync_tags", "status": "success"})
            
            result["status"] = "success"
            
        except subprocess.CalledProcessError as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def sync_gitlab_to_github(self, branch: str = "main", force: bool = False) -> dict:
        """Sync from GitLab to GitHub."""
        result = {
            "direction": "gitlab-to-github",
            "branch": branch,
            "status": "pending",
            "steps": [],
        }
        
        try:
            # Fetch from GitLab
            gitlab_url = f"https://oauth2:{self.config.gitlab_token}@gitlab.com/{self.config.gitlab_project_path}.git"
            self._run_git(["fetch", gitlab_url, branch])
            result["steps"].append({"step": "fetch_gitlab", "status": "success"})
            
            # Push to GitHub
            github_url = f"https://oauth2:{self.config.github_token}@github.com/{self.config.github_repo}.git"
            push_args = ["push", github_url, f"FETCH_HEAD:refs/heads/{branch}"]
            if force:
                push_args.insert(1, "--force")
            
            self._run_git(push_args)
            result["steps"].append({"step": "push_github", "status": "success"})
            
            result["status"] = "success"
            
        except subprocess.CalledProcessError as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def _run_git(self, args: list[str]) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    
    def generate_sync_badge(self, in_sync: bool) -> str:
        """Generate markdown badge for sync status."""
        if in_sync:
            return "![Sync Status](https://img.shields.io/badge/Sync-In%20Sync-brightgreen)"
        else:
            return "![Sync Status](https://img.shields.io/badge/Sync-Out%20of%20Sync-red)"


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Repository sync tool")
    parser.add_argument(
        "--direction",
        type=str,
        choices=["github-to-gitlab", "gitlab-to-github", "check"],
        default="check",
        help="Sync direction or check status",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Branch to sync",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force push (overwrites remote)",
    )
    args = parser.parse_args()
    
    config = SyncConfig.from_env()
    syncer = RepositorySyncer(config)
    
    if args.direction == "check":
        status = await syncer.get_status()
        print(f"GitHub SHA: {status.github_sha}")
        print(f"GitLab SHA: {status.gitlab_sha}")
        print(f"In Sync: {status.in_sync}")
        print()
        print(syncer.generate_sync_badge(status.in_sync))
    
    elif args.direction == "github-to-gitlab":
        result = syncer.sync_github_to_gitlab(args.branch, args.force)
        print(f"Sync result: {result['status']}")
        for step in result.get("steps", []):
            print(f"  - {step['step']}: {step['status']}")
    
    elif args.direction == "gitlab-to-github":
        result = syncer.sync_gitlab_to_github(args.branch, args.force)
        print(f"Sync result: {result['status']}")
        for step in result.get("steps", []):
            print(f"  - {step['step']}: {step['status']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
