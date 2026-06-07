#!/usr/bin/env python3
"""Build Strata artifacts and serve a local HTML observability dashboard."""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.outputs import write_artifacts
from strata.outputs.dashboard import build_dashboard_html
from strata.pipeline import build_graph, build_graph_from_looker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Path to a LookML repo or fixture directory")
    parser.add_argument("--usage-fixture", help="Fixture JSON")
    parser.add_argument("--looker-url", help="Looker instance URL for live System Activity enrichment")
    parser.add_argument("--client-id", help="Reserved for explicit admin client auth fallback")
    parser.add_argument("--client-secret", help="Reserved for explicit admin client auth fallback")
    parser.add_argument("--days", type=int, default=30, help="Live Looker usage window in days (default 30)")
    parser.add_argument("--schema-fixture", help="Optional L1 schema facts JSON")
    parser.add_argument("--out", help="Output directory (default: output/<repo-name>/)")
    parser.add_argument("--port", type=int, default=8765, help="Local server port (default 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Skip opening the browser")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists():
        parser.error(f"--repo does not exist: {repo}")

    out_dir = Path(args.out).expanduser().resolve() if args.out else REPO_ROOT / "output" / repo.name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building IR for {repo.name}...")
    if args.looker_url:
        if args.client_id or args.client_secret:
            parser.error("--client-id/--client-secret fallback is reserved; use scripts/strata_auth.py login")
        graph = build_graph_from_looker(repo, args.looker_url, args.days, args.schema_fixture)
    else:
        graph = build_graph(repo, args.usage_fixture, args.schema_fixture)

    print("Writing artifacts...")
    artifacts = write_artifacts(graph, out_dir)

    print("Generating dashboard...")
    import json
    artifact_data = {
        name: json.loads(Path(path).read_text(encoding="utf-8"))
        for name, path in artifacts.items()
    }
    html = build_dashboard_html(artifact_data, graph)
    dashboard_path = out_dir / "dashboard.html"
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {dashboard_path}")

    url = f"http://localhost:{args.port}/dashboard.html"
    print(f"\nServing at {url}  (Ctrl+C to stop)\n")

    os.chdir(out_dir)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # silence request logs

    socketserver.TCPServer.allow_reuse_address = True
    server = http.server.HTTPServer(("localhost", args.port), handler)

    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=[url]).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
