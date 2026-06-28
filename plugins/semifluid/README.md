# Semifluid Codex Plugin

This is the installable Codex plugin bundle for Semifluid.

## Contents

- `.codex-plugin/plugin.json`: required Codex plugin manifest.
- `.mcp.json`: OAuth bootstrap for Semifluid plugin authentication.
- `skills/semifluid/SKILL.md`: Codex guidance for API-first Semifluid retrieval and mutations.
- `scripts/semifluid_api.py`: standard-library Semifluid HTTP API helper.
- `references/api-reference.md`: local endpoint reference copied from the v1 API skill.

## Install

Install this plugin through the repository marketplace from the repository root:

```bash
codex plugin marketplace add /Users/jpamorgan/Development/semifluid-integrations
```

Or from GitHub:

```bash
codex plugin marketplace add jpamorgan/semifluid-integrations
```

Then open Codex, choose the `Semifluid Integrations` marketplace, install `Semifluid`, authenticate
with Semifluid, and start a new thread.

## API Helper

Semifluid operations should use the bundled helper:

```bash
python3 scripts/semifluid_api.py health
python3 scripts/semifluid_api.py auth login
python3 scripts/semifluid_api.py get /v1/collections
python3 scripts/semifluid_api.py collections list --names
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=10 --query fields='*'
```

The helper sends `Authorization: Bearer <token>` by default. `collections list` follows pagination
automatically, and `--names` emits only collection names for name-only requests. Run `auth login`
once to authorize via Semifluid OAuth; the helper stores credentials in a local cache and refreshes
access tokens when possible. For automation, the helper also accepts explicit bearer token
overrides from `SEMIFLUID_ACCESS_TOKEN`, `SEMIFLUID_OAUTH_TOKEN`, or
`CODEX_SEMIFLUID_ACCESS_TOKEN`.

## Plugin Authoring Notes

- The folder name, manifest `name`, marketplace plugin entry, and skill namespace should stay
  aligned as `semifluid`.
- Keep bundled plugin files at the plugin root, except for `.codex-plugin/plugin.json`.
- Keep `.mcp.json` only for Codex plugin OAuth bootstrap. The API helper owns a separate OAuth
  authorization-code cache for direct shell API calls.
- Keep starter prompts short and limit them to the first three useful examples.
- Restart Codex and test in a fresh thread after changing manifest, skill, script, or auth config
  files.
