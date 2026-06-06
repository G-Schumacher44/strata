#!/usr/bin/env python3
"""Manage local Strata Looker OAuth token state."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from strata.l1.looker import DEFAULT_CLIENT_GUID, DEFAULT_REDIRECT_URI, DEFAULT_TOKEN_PATH, auth_url, exchange_code, load_token, save_token


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    login = subparsers.add_parser("login", help="Exchange a Looker OAuth authorization code")
    login.add_argument("--looker-url", required=True)
    login.add_argument("--code", help="Authorization code copied from the localhost redirect")
    login.add_argument("--client-guid", default=DEFAULT_CLIENT_GUID)
    login.add_argument("--redirect-uri", default=DEFAULT_REDIRECT_URI)
    login.add_argument("--token-path", default=str(DEFAULT_TOKEN_PATH))
    login.add_argument("--no-browser", action="store_true", help="Print auth URL without opening a browser")

    status = subparsers.add_parser("status", help="Print redacted local token status")
    status.add_argument("--token-path", default=str(DEFAULT_TOKEN_PATH))

    logout = subparsers.add_parser("logout", help="Delete local token state")
    logout.add_argument("--token-path", default=str(DEFAULT_TOKEN_PATH))

    args = parser.parse_args()
    if args.command == "login":
        url = auth_url(args.looker_url, args.client_guid, args.redirect_uri)
        print(url)
        if not args.no_browser:
            webbrowser.open(url)
        if not args.code:
            print("Open the URL, authorize Strata, then re-run with --code from the redirect.", file=sys.stderr)
            return 2
        token = exchange_code(args.looker_url, args.code, args.client_guid, args.redirect_uri)
        save_token(token, args.token_path)
        print(json.dumps(token.redacted(), indent=2, sort_keys=True))
        return 0
    if args.command == "status":
        token = load_token(args.token_path)
        print(json.dumps(token.redacted(), indent=2, sort_keys=True))
        return 0
    if args.command == "logout":
        path = Path(args.token_path).expanduser()
        if path.exists():
            path.unlink()
        print(f"Removed {path}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
