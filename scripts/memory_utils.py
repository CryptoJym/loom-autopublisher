#!/usr/bin/env python3
"""Utilities for working with Mem0 hierarchical memory.

Provides AgentMemory helper that lets any script or agent store and query
memories with explicit isolation levels:
    repo                -> <repo>
    repo+agent          -> <repo>:<agent>
    repo+issue          -> <repo>:<issue>
    repo+agent+issue    -> <repo>:<agent>:<issue>

Agents should depend on the narrowest level first and broaden on fallback.
"""
from __future__ import annotations
import os
import subprocess
from typing import Any, Dict, List, Optional

try:
    from mem0 import MemoryClient  # type: ignore
except ImportError:  # graceful degradation when mem0ai not installed locally
    MemoryClient = None  # type: ignore

# -----------------------------------------------------------------------------
# helper
# -----------------------------------------------------------------------------

def _current_branch() -> str:
    """Return current git branch or 'main' if unavailable."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True)
            .strip()
        )
    except Exception:
        return "main"


def _extract_issue_id(branch: str) -> str:
    """Extract ISSUE-123 id from branch names like feat/ISSUE-123-foo."""
    if branch.startswith("feat/"):
        parts = branch.split("/")[1].split("-")
        if len(parts) >= 2 and parts[0].upper() == "ISSUE":
            return parts[1]
    return "none"


class AgentMemory:
    """Wrapper around Mem0 MemoryClient with contextual isolation."""

    def __init__(
        self,
        agent_name: Optional[str] = None,
        repo_name: Optional[str] = None,
        branch: Optional[str] = None,
        issue_id: Optional[str] = None,
    ) -> None:
        # fallback values
        self.repo_name = repo_name or os.getenv("REPO_NAME") or os.path.basename(os.getcwd())
        self.branch = branch or os.getenv("BRANCH_NAME") or _current_branch()
        self.issue_id = issue_id or _extract_issue_id(self.branch)
        self.agent_name = agent_name or os.getenv("AGENT_NAME") or "unknown"

        self.client = MemoryClient() if (MemoryClient and os.getenv("MEM0_API_KEY")) else None

    # ------------------------------------------------------------------
    # user_id helpers
    # ------------------------------------------------------------------
    def _user_id(self, level: str) -> str:
        if level == "repo":
            return self.repo_name
        if level == "repo+agent":
            return f"{self.repo_name}:{self.agent_name}"
        if level == "repo+issue":
            return f"{self.repo_name}:{self.issue_id}"
        # default full isolation
        return f"{self.repo_name}:{self.agent_name}:{self.issue_id}"

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def add(
        self,
        content: str | List[Dict[str, str]],
        isolation_level: str = "repo+agent+issue",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self.client:
            return False
        meta = {
            "repo": self.repo_name,
            "agent": self.agent_name,
            "branch": self.branch,
            "issue_id": self.issue_id,
            **(metadata or {}),
        }
        try:
            self.client.add(content, user_id=self._user_id(isolation_level), metadata=meta)
            return True
        except Exception:
            return False

    def search(
        self,
        query: str,
        isolation_level: str = "repo+agent+issue",
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            return self.client.search(
                query,
                user_id=self._user_id(isolation_level),
                limit=limit,
                filters=filters or {},
            )
        except Exception:
            return []
