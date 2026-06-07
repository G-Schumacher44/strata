"""strata bootstrap — drop full governance into any repo."""
from __future__ import annotations

import json
from pathlib import Path

import click


@click.command("bootstrap")
@click.option("--repo", default=".", show_default=True, help="Target repo path")
@click.option("--no-git", is_flag=True, help="Skip .gitignore update")
@click.option("--no-conductor", is_flag=True, help="Skip conductor/ setup")
@click.option("--no-mcp", is_flag=True, help="Skip .mcp.json / .cursor/mcp.json")
@click.option("--force", is_flag=True, help="Overwrite existing files")
def bootstrap(
    repo: str,
    no_git: bool,
    no_conductor: bool,
    no_mcp: bool,
    force: bool,
) -> None:
    """Drop full Strata governance into a repo and prep the environment."""
    target = Path(repo).expanduser().resolve()
    if not target.exists():
        raise click.ClickException(f"Repo path does not exist: {target}")

    tpl_root = Path(__file__).resolve().parent.parent / "bootstrap" / "templates"
    project = target.name

    click.secho(f"Bootstrapping Strata governance into: {target}", bold=True)
    click.echo("")

    # --- .gitignore ---
    if not no_git:
        _append_gitignore(target, tpl_root)

    # --- AGENTS.md ---
    _write_file(
        target / "AGENTS.md",
        tpl_root / "AGENTS.md",
        subs={"{{PROJECT_NAME}}": project},
        force=force,
    )

    # --- CLAUDE.md ---
    _write_file(
        target / "CLAUDE.md",
        tpl_root / "CLAUDE.md",
        subs={"{{PROJECT_NAME}}": project},
        force=force,
    )

    # --- conductor/ ---
    if not no_conductor:
        from strata.cli.conductor import conductor_init
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(conductor_init, ["--repo", str(target)] + (["--force"] if force else []))
        click.echo(result.output.rstrip())

    # --- .mcp.json ---
    if not no_mcp:
        _write_mcp_configs(target, tpl_root, project, force)

    # --- ~/.strata/config.json ---
    _prompt_strata_config(target)

    click.echo("")
    click.secho("Bootstrap complete.", fg="green")
    click.echo("Next: strata mcp validate")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _append_gitignore(target: Path, tpl_root: Path) -> None:
    gitignore = target / ".gitignore"
    new_block = (tpl_root / "gitignore.append").read_text(encoding="utf-8")

    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")
        if "# Strata" in existing:
            click.echo("  skip (already present): .gitignore Strata block")
            return
        gitignore.write_text(existing.rstrip() + "\n\n" + new_block, encoding="utf-8")
        click.secho("  appended: .gitignore", fg="green")
    else:
        gitignore.write_text(new_block, encoding="utf-8")
        click.secho("  wrote: .gitignore", fg="green")


def _write_file(
    dest: Path,
    src: Path,
    subs: dict[str, str] | None = None,
    force: bool = False,
) -> None:
    if dest.exists() and not force:
        click.echo(f"  skip (exists): {dest.name}  (use --force to overwrite)")
        return
    content = src.read_text(encoding="utf-8")
    if subs:
        for k, v in subs.items():
            content = content.replace(k, v)
    dest.write_text(content, encoding="utf-8")
    click.secho(f"  wrote: {dest.name}", fg="green")


def _write_mcp_configs(target: Path, tpl_root: Path, project: str, force: bool) -> None:
    import sys

    strata_mcp_cmd = str(Path(sys.executable).parent / "strata-mcp")
    subs = {
        "{{PROJECT_NAME}}": project,
        "{{REPO_PATH}}": str(target),
        "{{STRATA_MCP_CMD}}": strata_mcp_cmd,
    }

    mcp_json = target / ".mcp.json"
    _write_file(mcp_json, tpl_root / "mcp.json", subs, force)

    cursor_dir = target / ".cursor"
    cursor_dir.mkdir(exist_ok=True)
    _write_file(cursor_dir / "mcp.json", tpl_root / "cursor_mcp.json", subs, force)


def _prompt_strata_config(target: Path) -> None:
    config_path = Path.home() / ".strata" / "config.json"
    if config_path.exists():
        click.echo(f"\n  ~/.strata/config.json already exists — skipping prompt.")
        return

    click.echo("")
    if not click.confirm("Set up ~/.strata/config.json now?", default=True):
        click.echo("  Skipped. Create ~/.strata/config.json manually when ready.")
        return

    repo_path = click.prompt("  LookML repo path", default=str(target))
    bq_project = click.prompt("  BigQuery project (or leave blank)", default="", show_default=False)

    cfg: dict = {"repo_path": repo_path}
    if bq_project:
        cfg["bq_project"] = bq_project

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    click.secho(f"  wrote: {config_path}", fg="green")
