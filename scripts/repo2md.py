#!/usr/bin/env python3
"""Walk the repo and emit a single markdown file showing changed source only."""
import pathlib, sys, hashlib, os
root = pathlib.Path(__file__).resolve().parents[1]
EXCLUDE = {".git", "context", ".github", ".venv"}

# --- hierarchical context helpers -------------------------------------------------
import subprocess, hashlib

def get_repo_context():
    ctx = {
        "repo_name": os.getenv("REPO_NAME") or pathlib.Path(__file__).resolve().parents[1].name,
        "branch": os.getenv("BRANCH_NAME") or "unknown",
        "issue_id": "none",
    }
    # git branch if available
    try:
        ctx["branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
    except Exception:
        pass
    # parse issue id
    if ctx["branch"].startswith("feat/"):
        parts = ctx["branch"].split("/")[1].split("-")
        if len(parts) >= 2 and parts[0].upper() == "ISSUE":
            ctx["issue_id"] = parts[1]
    return ctx

repo_ctx = get_repo_context()

# Initialize Mem0 via helper
try:
    from scripts.memory_utils import AgentMemory  # type: ignore
    MEMORY = AgentMemory(
        agent_name="snapshot-bot",
        repo_name=repo_ctx["repo_name"],
        branch=repo_ctx["branch"],
        issue_id=repo_ctx["issue_id"],
    )
except Exception:
    MEMORY = None

print("<!---- AUTO-GENERATED: do not edit by hand -->")
for path in root.rglob("*.*"):
    if any(part in EXCLUDE for part in path.parts):
        continue
    if path.stat().st_size > 50_000:  # skip binaries & huge assets
        continue
    rel = path.relative_to(root)
    code = path.read_text(errors="ignore")
    sha  = hashlib.sha1(code.encode()).hexdigest()[:8]
    # Push to Mem0 if configured
    if MEMORY:
        try:
            # Store code with basic path/sha context if supported
            MEMORY.add(
                code,
                isolation_level="repo+issue",  # snapshot shared per issue
                metadata={"path": str(rel), "sha": sha},
            )
        except Exception:
            pass
    print(f"\n## {rel}  \[{sha}]\n```{rel.suffix.lstrip('.')}\n{code}\n```")
