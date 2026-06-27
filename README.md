# Semifluid Integrations

Codex plugin package and ChatGPT app package for Semifluid.

## Repository Layout

This repository is already organized as a repo-scoped Codex marketplace, so no file reorganization
is needed.

```text
.agents/plugins/marketplace.json      # Codex marketplace catalog
plugins/semifluid/                    # Installable Codex plugin bundle
  .codex-plugin/plugin.json           # Required plugin manifest
  .mcp.json                           # OAuth bootstrap for plugin authentication
  skills/semifluid/SKILL.md           # Codex API-first agent guidance
  scripts/semifluid_api.py            # Bundled Semifluid HTTP API helper
  references/api-reference.md         # Local API endpoint reference
apps/chatgpt/                         # ChatGPT app setup and review notes
```

This layout follows the current Codex plugin convention: each plugin bundle lives under
`plugins/<plugin-name>`, only the manifest lives in `.codex-plugin/`, and the repo-level
marketplace points to installable bundles with `./`-prefixed relative paths.

Reference: [OpenAI Codex plugin docs](https://developers.openai.com/codex/plugins/build).

## Install In Codex

Add the marketplace from GitHub:

```bash
codex plugin marketplace add jpamorgan/semifluid-integrations
```

For local development from this checkout:

```bash
codex plugin marketplace add /Users/jpamorgan/Development/semifluid-integrations
```

Then restart Codex or open the plugin directory, choose the `Semifluid Integrations` marketplace,
and install `Semifluid`.

After installation, authenticate with Semifluid and start a new Codex thread so the bundled skill is
loaded in the thread context.

## Verify Installation

In a new Codex thread, ask for a Semifluid operation such as:

```text
Search my Semifluid collections for customer records.
```

The thread should load the `semifluid` skill and use the bundled API helper:

```bash
python3 scripts/semifluid_api.py get /v1/collections
```

If the helper reports a missing OAuth token, authorize the API helper:

```bash
python3 plugins/semifluid/scripts/semifluid_api.py auth login
```

## Semifluid Codex Plugin

The Codex plugin bundle is in `plugins/semifluid`.

It provides:

- A plugin manifest with install-surface metadata.
- A bundled Semifluid API helper copied from the v1 API skill and updated for OAuth bearer auth.
- A Codex skill that tells agents when and how to use direct Semifluid HTTP API calls.
- A Semifluid MCP declaration retained as the plugin OAuth bootstrap.

When changing the plugin, keep the manifest name, folder name, and marketplace entry name aligned:
`semifluid`.

## ChatGPT App

The ChatGPT app package is in `apps/chatgpt`.

ChatGPT does not consume Codex `SKILL.md` files. ChatGPT learns how to use an app from the remote
MCP server: server instructions, tool names, tool descriptions, schemas, annotations, OAuth
metadata, and optional widget metadata. The files in `apps/chatgpt` are maintainer-facing setup and
submission artifacts for the hosted MCP endpoint.

Use this MCP server URL when connecting the app in ChatGPT developer mode:

```text
https://api.semifluid.ai/mcp
```

## Semifluid API Helper

The Codex plugin should operate through:

```bash
python3 plugins/semifluid/scripts/semifluid_api.py health
python3 plugins/semifluid/scripts/semifluid_api.py auth login
python3 plugins/semifluid/scripts/semifluid_api.py get /v1/collections
python3 plugins/semifluid/scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=10 --query fields='*'
python3 plugins/semifluid/scripts/semifluid_api.py post /v1/collections/{collectionId}/records/query --json @query.json
```

The helper sends bearer auth by default. Run `auth login` once to authorize through Semifluid OAuth;
the helper stores credentials in a local cache and refreshes access tokens when possible. For
automation, the helper also accepts explicit bearer token overrides from `SEMIFLUID_ACCESS_TOKEN`,
`SEMIFLUID_OAUTH_TOKEN`, or `CODEX_SEMIFLUID_ACCESS_TOKEN`.

## Maintenance Checklist

- Keep `.agents/plugins/marketplace.json` as the repo marketplace catalog.
- Keep installable Codex plugin bundles under `plugins/<plugin-name>`.
- Keep `skills/`, `.mcp.json`, `.app.json`, `hooks/`, and `assets/` at the plugin root.
- Keep only `.codex-plugin/plugin.json` inside `.codex-plugin/`.
- Use relative manifest paths that start with `./`.
- Keep `.mcp.json` in the `mcpServers` companion shape while it is needed for plugin OAuth
  bootstrap.
- Keep marketplace `source.path` relative to the repository root.
- Restart Codex and test in a new thread after plugin metadata, skill, helper, or auth config
  changes.
