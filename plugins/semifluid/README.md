# Semifluid Codex Plugin

This is the installable Codex plugin bundle for Semifluid.

## Contents

- `.codex-plugin/plugin.json`: required Codex plugin manifest.
- `.mcp.json`: OAuth bootstrap for Semifluid plugin authentication.
- `skills/semifluid/SKILL.md`: Codex guidance for Semifluid retrieval and mutations.
- `scripts/semifluid_api.py`: standard-library Semifluid HTTP API helper for public endpoints and
  explicit compatibility credentials.
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
python3 scripts/semifluid_api.py get /v1/collections
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=10 --query fields='*'
```

Codex MCP OAuth authenticates plugin tool calls but does not expose plugin access tokens to helper
subprocesses. For direct shell API calls, set `SEMIFLUID_ACCESS_TOKEN`, `SEMIFLUID_OAUTH_TOKEN`, or
`CODEX_SEMIFLUID_ACCESS_TOKEN` explicitly. API-key auth is available only as compatibility mode with
`SEMIFLUID_API_KEY --auth-header x-api-key`.

## Plugin Authoring Notes

- The folder name, manifest `name`, marketplace plugin entry, and skill namespace should stay
  aligned as `semifluid`.
- Keep bundled plugin files at the plugin root, except for `.codex-plugin/plugin.json`.
- Keep `.mcp.json` only for plugin OAuth bootstrap unless Codex adds a first-class script OAuth
  mechanism.
- Keep starter prompts short and limit them to the first three useful examples.
- Restart Codex and test in a fresh thread after changing manifest, skill, script, or auth config
  files.
