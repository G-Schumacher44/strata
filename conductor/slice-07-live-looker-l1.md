# Slice 07: Live Looker L1 Adapter

Date: 2026-06-06
Status: blocked
Brick: post-v0.1.0
Depends: Slice 06 STABLE; read-only test-instance credentials/access

```yaml
conductor_mode: slice
context_budget: medium
handoff_required: true
stable_tag_required: false
```

## Objective

Wire the Slice 06 provider boundary to read-only live Looker/System Activity facts
on the test instance. This slice is blocked until test-instance access is available.

## Blocker

Need read-only Looker test-instance access and OAuth client registration.

Preferred auth route:

- Register Strata as a Looker OAuth client app using Looker's OAuth client app API.
- Use a stable `client_guid`, recommended: `com.gsanalytics.strata.cli`.
- Use a localhost redirect URI for CLI/MCP development, recommended:
  `http://localhost:8765/oauth/callback`.
- Restrict use with `group_id` when available.
- Store access tokens only in local ignored storage or OS keychain.
- Do not commit secrets and do not make API client-secret auth the default path.
- API client ID/secret auth may exist only as an explicit admin-run fallback, not the
  default trust model.

The live provider should use OAuth tokens to call read-only Looker/System Activity
endpoints and return the Slice 06 provider dataclasses.

## OAuth Implementation Plan

1. Add `strata auth login` or equivalent script that starts a localhost callback server.
2. Redirect the browser to the Looker UI `/auth` endpoint with the registered
   `client_guid` and exact `redirect_uri`.
3. Exchange the returned code at the Looker API `/token` endpoint.
4. Store token state locally with redacted `auth status` output.
5. Keep ordinary CI fixture/replay-only; live smoke remains manual and opt-in.

## Acceptance Criteria

- [ ] Live adapter implements the Slice 06 provider protocol
- [ ] Missing live config fails fast with a clear message
- [ ] OAuth client_guid + redirect_uri config is documented and redacted in status output
- [ ] Token storage is local-only and ignored/keychain-backed
- [ ] Fixture/replay tests still pass without live Looker credentials
- [ ] Manual smoke command can fetch read-only test-instance facts
- [ ] No live dependency in ordinary CI
- [ ] `conductor/handoff-log.md` updated with a real Commit: hash
