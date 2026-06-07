"""strata dashboard — build artifacts and serve observability dashboard."""
from __future__ import annotations

import http.server
import json
import socketserver
import threading
import webbrowser
from pathlib import Path

import click


@click.command("dashboard")
@click.option("--repo", required=True, help="Path to LookML repo")
@click.option("--usage-fixture", default=None, help="Usage facts JSON")
@click.option("--schema-fixture", default=None, help="Schema facts JSON")
@click.option("--looker-url", default=None, help="Looker URL for live enrichment")
@click.option("--days", default=30, show_default=True, help="Looker usage window in days")
@click.option("--out", default=None, help="Output directory (default: output/<repo-name>)")
@click.option("--port", default=8765, show_default=True, help="Local server port")
@click.option("--no-browser", is_flag=True, help="Skip opening the browser")
def dashboard(
    repo: str,
    usage_fixture: str | None,
    schema_fixture: str | None,
    looker_url: str | None,
    days: int,
    out: str | None,
    port: int,
    no_browser: bool,
) -> None:
    """Build Strata artifacts and serve a local observability dashboard."""
    from strata.outputs import write_artifacts
    from strata.outputs.dashboard import build_dashboard_html
    from strata.pipeline import build_graph, build_graph_from_looker

    _repo = Path(repo).expanduser().resolve()
    out_dir = Path(out).expanduser().resolve() if out else Path.cwd() / "output" / _repo.name
    out_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Building IR for {_repo.name}...")
    if looker_url:
        graph = build_graph_from_looker(str(_repo), looker_url, days, schema_fixture)
    else:
        graph = build_graph(str(_repo), usage_fixture, schema_fixture)

    click.echo("Writing artifacts...")
    artifacts = write_artifacts(graph, str(out_dir))

    click.echo("Generating dashboard...")
    artifact_data = {
        name: json.loads(Path(path).read_text(encoding="utf-8"))
        for name, path in artifacts.items()
    }
    html = build_dashboard_html(artifact_data, graph)
    dashboard_path = out_dir / "dashboard.html"
    dashboard_path.write_text(html, encoding="utf-8")
    click.secho(f"Dashboard: {dashboard_path}", fg="green")

    url = f"http://localhost:{port}/dashboard.html"
    click.echo(f"\nServing at {url}  (Ctrl+C to stop)\n")

    import os
    os.chdir(out_dir)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None
    socketserver.TCPServer.allow_reuse_address = True
    server = http.server.HTTPServer(("localhost", port), handler)

    if not no_browser:
        threading.Timer(0.4, webbrowser.open, args=[url]).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nStopped.")
