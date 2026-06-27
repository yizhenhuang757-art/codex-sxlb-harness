#!/usr/bin/env python3
"""Low-risk health checks for external capabilities used by SXLB."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


LEGAL_STATUSES = {"ok", "missing", "auth-expired", "unhealthy", "rate-limited", "unknown"}


def command_exists(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def status_item(capability: str, status: str, detail: str, fallback: str, action: str) -> dict[str, str]:
    if status not in LEGAL_STATUSES:
        status = "unknown"
    return {
        "capability": capability,
        "status": status,
        "detail": detail,
        "recommended_fallback": fallback,
        "user_action": action,
    }


def check_agent_reach() -> dict[str, str]:
    skills_home = Path(os.environ.get("CODEX_SKILLS_HOME", str(Path.home() / ".agents" / "skills")))
    skill = skills_home / "agent-reach" / "SKILL.md"
    if skill.exists():
        return status_item("agent-reach", "ok", str(skill), "use web search or platform-specific manual route", "none")
    return status_item("agent-reach", "missing", "agent-reach skill not found", "use web search", "install or restore agent-reach skill if needed")


def check_opencli() -> dict[str, str]:
    found = command_exists("opencli")
    if found:
        return status_item("opencli", "ok", found, "use direct web/search tooling", "none")
    return status_item("opencli", "missing", "opencli command not found", "use direct web/search tooling", "install or expose opencli on PATH")


def check_github_cli() -> dict[str, str]:
    found = command_exists("gh")
    if not found:
        return status_item("github-cli", "missing", "gh command not found", "use local git/filesystem evidence", "install GitHub CLI and authenticate")
    result = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True, check=False, timeout=10)
    combined = f"{result.stdout}\n{result.stderr}".lower()
    if result.returncode == 0:
        return status_item("github-cli", "ok", "gh auth status succeeded", "use local git/filesystem evidence", "none")
    if "not logged" in combined or "not authenticated" in combined or "authentication" in combined:
        return status_item("github-cli", "auth-expired", "gh auth status indicates authentication is missing or expired", "use local git/filesystem evidence", "run gh auth login")
    if "rate limit" in combined:
        return status_item("github-cli", "rate-limited", "gh auth status reported rate limiting", "retry later or use local evidence", "wait and retry")
    return status_item("github-cli", "unhealthy", "gh exists but auth status failed", "use local git/filesystem evidence", "inspect gh auth status")


def check_chrome() -> dict[str, str]:
    app = Path("/Applications/Google Chrome.app")
    binary = command_exists("google-chrome", "chromium", "chrome")
    if app.exists() or binary:
        return status_item("chrome", "ok", str(app if app.exists() else binary), "use non-browser HTTP/search tooling", "none")
    return status_item("chrome", "missing", "Chrome app/binary not found", "use non-browser HTTP/search tooling", "install Chrome or configure browser MCP")


def check_mcp() -> dict[str, str]:
    home = Path.home()
    candidates = [
        Path(os.environ.get("CODEX_HOME", str(home / ".codex"))) / "mcp.json",
        home / ".config" / "codex" / "mcp.json",
        home / ".cursor" / "mcp.json",
        home / ".claude" / "mcp.json",
    ]
    existing = [str(path) for path in candidates if path.exists()]
    if existing:
        return status_item("mcp", "ok", ", ".join(existing), "use direct CLI/browser tooling", "none")
    return status_item("mcp", "unknown", "no known MCP config file found", "use direct CLI/browser tooling", "confirm MCP config location if MCP is needed")


def health_report() -> dict[str, object]:
    checks = [check_agent_reach(), check_opencli(), check_github_cli(), check_chrome(), check_mcp()]
    return {"ok": True, "capabilities": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Report low-risk external capability health.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    report = health_report()
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report["capabilities"]:
            print(f"{item['capability']}: {item['status']} ({item['detail']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
