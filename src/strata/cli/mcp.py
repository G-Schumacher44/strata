"""strata mcp — MCP server controls."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from strata.config import load_repo_path


@click.group()
def mcp() -> None:
    """Local MCP server for AI clients (Claude, Cursor, Gemini).

    Exposes 14 read-only LookML analysis tools over stdio. Configure your
    AI client to launch `strata-mcp` via .mcp.json, then ask it to audit
    dead code, PDT costs, schema drift, or explore dependencies.
    """


@mcp.command("run")
def mcp_run() -> None:
    """Start the MCP server (used by .mcp.json / AI client configs).

    Runs in the foreground over stdio. Normally launched by your AI client
    automatically — you don't need to run this manually unless debugging.
    Set STRATA_REPO_PATH to point at your LookML repo.
    """
    from strata.mcp.server import main
    main()


@mcp.command("validate")
def mcp_validate() -> None:
    """Check repo path, IR cache, bundled skills, and Looker token.

    Run this after `strata bootstrap` to confirm everything is wired up
    before opening your AI client.
    """
    ok = True

    # Repo path
    repo = _repo_path()
    click.echo(f"  repo:       {repo}")
    if not repo.exists():
        click.secho("  ✗ repo path does not exist", fg="red")
        ok = False
    else:
        click.secho("  ✓ repo path exists", fg="green")

    # IR cache
    cache = repo / "strata_ir.db"
    if cache.exists():
        import time
        age = int(time.time() - cache.stat().st_mtime)
        click.secho(f"  ✓ IR cache found (age: {age}s)", fg="green")
    else:
        click.secho("  ✗ IR cache not found — run `make build` or `strata outputs`", fg="yellow")

    # Skills
    try:
        skills_dir = Path(__file__).resolve().parent.parent / "skills"
        skill_count = len(list(skills_dir.rglob("SKILL.md")))
        click.secho(f"  ✓ skills: {skill_count} found", fg="green")
    except OSError as e:
        click.secho(f"  ✗ skills not found: {e}", fg="red")
        ok = False

    # Chart templates
    try:
        charts_dir = Path(__file__).resolve().parent.parent / "viz" / "charts"
        chart_count = len(list(charts_dir.glob("*.yml")))
        click.secho(f"  ✓ chart templates: {chart_count} found", fg="green")
    except OSError as e:
        click.secho(f"  ✗ chart templates not found: {e}", fg="red")
        ok = False

    # Looker token
    token_path = Path.home() / ".strata" / "looker_token.json"
    if token_path.exists():
        click.secho("  ✓ Looker token present", fg="green")
    else:
        click.secho("  ✗ Looker token missing — run `strata auth login`", fg="yellow")

    click.echo()
    if ok:
        click.secho("MCP server is ready.", fg="green", bold=True)
    else:
        click.secho("Issues found — see above.", fg="red", bold=True)
        sys.exit(1)


@mcp.command("config")
def mcp_config() -> None:
    """Show resolved paths and env vars the MCP server will use."""
    repo = _repo_path()
    config = {
        "repo_path": str(repo),
        "skills_path": os.environ.get("STRATA_SKILLS_PATH", "(bundled)"),
        "charts_path": os.environ.get("STRATA_CHARTS_PATH", "(bundled)"),
        "conductor_path": os.environ.get("STRATA_CONDUCTOR_PATH", str(repo / "conductor")),
        "cache_path": os.environ.get("STRATA_CACHE_PATH", str(repo / "strata_ir.db")),
        "usage_fixture": os.environ.get("STRATA_USAGE_FIXTURE", "(none)"),
        "schema_fixture": os.environ.get("STRATA_SCHEMA_FIXTURE", "(none)"),
    }
    click.echo(json.dumps(config, indent=2))


def _repo_path() -> Path:
    return load_repo_path()
