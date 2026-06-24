# Semifluid Integrations

Codex plugin package and ChatGPT app package for Semifluid integrations.

## Contents

- `plugins/semifluid`: Codex plugin bundle.
- `.agents/plugins/marketplace.json`: Local marketplace entry for the Semifluid plugin.
- `apps/chatgpt`: ChatGPT app package notes for the hosted Semifluid MCP endpoint.

## Install

From GitHub:

```bash
codex plugin marketplace add jpamorgan/semifluid-integrations
```

For local development from this repository root:

```bash
codex plugin marketplace add /Users/jpamorgan/Development/semifluid-integrations
```

Then open the Semifluid plugin in Codex and install it from the `semifluid-integrations`
marketplace.

## Semifluid Plugin

The bundled plugin provides:

- A Semifluid MCP server declaration for `https://api.semifluid.ai/mcp`.
- A Codex skill that instructs agents how to use the Semifluid MCP tools.

## ChatGPT App

The ChatGPT app package is in `apps/chatgpt`.

ChatGPT does not consume Codex `SKILL.md` files. ChatGPT learns how to use an app from the
remote MCP server: server instructions, tool names, tool descriptions, schemas, annotations,
OAuth metadata, and optional widget metadata. The files in `apps/chatgpt` are maintainer-facing
setup and submission artifacts for the hosted MCP endpoint.

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
