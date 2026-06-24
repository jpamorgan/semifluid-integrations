# Semifluid Integrations

Codex plugin package and ChatGPT app package for the hosted Semifluid MCP endpoint.

## Repository Layout

This repository is already organized as a repo-scoped Codex marketplace, so no file reorganization
is needed.

```text
.agents/plugins/marketplace.json      # Codex marketplace catalog
plugins/semifluid/                    # Installable Codex plugin bundle
  .codex-plugin/plugin.json           # Required plugin manifest
  .mcp.json                           # Bundled Semifluid MCP server config
  skills/semifluid/SKILL.md           # Codex agent guidance
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

After installation, start a new Codex thread so the bundled skill and MCP server are loaded in the
thread context.

## Verify Installation

In a new Codex thread, ask for a Semifluid operation such as:

```text
Search my Semifluid collections for customer records.
```

The thread should load the `semifluid` skill and use the bundled MCP server at:

```text
https://api.semifluid.ai/mcp
```

If the Semifluid MCP tools are not visible, confirm the plugin is enabled in Codex, then restart the
thread after enabling it.

## Semifluid Codex Plugin

The Codex plugin bundle is in `plugins/semifluid`.

It provides:

- A plugin manifest with install-surface metadata.
- A bundled Semifluid MCP server declaration for `https://api.semifluid.ai/mcp`.
- A Codex skill that tells agents when and how to use the Semifluid MCP tools.

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

## MCP Tool Surface

The hosted Semifluid MCP currently exposes these tools:

| Tool | Access | Purpose |
| --- | --- | --- |
| `search` | Read-only | Search Semifluid collections by name and records by content. |
| `fetch` | Read-only | Fetch full text for a Semifluid collection or record returned by `search`. |
| `semifluid_collections` | Mutating | List, create, inspect, update, or delete Semifluid collections. |
| `semifluid_schema` | Mutating | Create, update, delete, or reorder fields and collection views. |
| `semifluid_records` | Mutating | List, query, aggregate, create, update, upsert, import, or delete records. |
| `semifluid_attachments` | Mutating | Upload attachments or retrieve authorized attachment metadata/content. |
| `semifluid_suggestions` | Mutating | List, create, inspect, approve, or reject record suggestions. |

The Codex skill directs agents to use `search` and `fetch` for retrieval, and the grouped tools for
intentional collection, schema, record, attachment, and suggestion operations with the required
OAuth scopes.

## Maintenance Checklist

- Keep `.agents/plugins/marketplace.json` as the repo marketplace catalog.
- Keep installable Codex plugin bundles under `plugins/<plugin-name>`.
- Keep `skills/`, `.mcp.json`, `.app.json`, `hooks/`, and `assets/` at the plugin root.
- Keep only `.codex-plugin/plugin.json` inside `.codex-plugin/`.
- Use relative manifest paths that start with `./`.
- Keep `.mcp.json` in the `mcpServers` companion shape validated by the local Codex plugin tooling.
- Keep marketplace `source.path` relative to the repository root.
- Restart Codex and test in a new thread after plugin metadata, skill, or MCP config changes.
