"""Shared configuration helpers — repo path, safe config parse."""
from __future__ import annotations

import json
import os
from pathlib import Path


def load_repo_path() -> Path:
    """Resolve repo path: STRATA_REPO_PATH env → ~/.strata/config.json → cwd."""
    env = os.environ.get("STRATA_REPO_PATH")
    if env:
        return Path(env).expanduser().resolve()
    config_path = Path.home() / ".strata" / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        if data.get("repo_path"):
            return Path(data["repo_path"]).expanduser().resolve()
    return Path.cwd().resolve()
