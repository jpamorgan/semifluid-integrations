# Semifluid ChatGPT App

This package documents the ChatGPT app that connects to the hosted Semifluid MCP server.

## App Archetype

`tool-only`

Semifluid currently exposes MCP tools only. There is no ChatGPT widget or MCP Apps UI resource in
this package, so no `text/html;profile=mcp-app` component template is registered here.

## MCP Server

Use the universal hosted MCP server URL:

```text
https://api.semifluid.ai/mcp
```

OAuth protected-resource metadata:

```text
https://api.semifluid.ai/.well-known/oauth-protected-resource
```

Authorization server:

```text
https://api.semifluid.ai/api/auth
```

## Skill Files

ChatGPT apps do not use Codex `SKILL.md` files.

Codex skills are local guidance for Codex agents. ChatGPT app behavior is driven by the MCP server
and the descriptors it returns: server instructions, tool names, descriptions, input/output schemas,
annotations, OAuth metadata, and optional UI resource metadata.

If ChatGPT needs different behavior, update the MCP server instructions and tool descriptors in the
Semifluid API service rather than adding a `SKILL.md` file to this package.

## Developer Mode Setup

1. Open ChatGPT.
2. Enable Developer Mode in Settings -> Apps & Connectors -> Advanced settings.
3. Add a new app/connector from the remote MCP server URL:
   `https://api.semifluid.ai/mcp`.
4. Complete the OAuth flow when ChatGPT prompts for Semifluid access.
5. Refresh the app metadata in ChatGPT after changing tool names, descriptions, schemas, or OAuth
   metadata on the server.

## Tool Surface

| Tool | Access | OAuth scopes | Purpose |
| --- | --- | --- | --- |
| `search` | Read-only | `collections:read`, `records:read` | Search Semifluid collections by name and records by content. |
| `fetch` | Read-only | `collections:read`, `records:read` | Fetch full text for a Semifluid collection or record returned by `search`. |
| `semifluid_collections` | Mutating | `collections:read`, `collections:write` | List, create, inspect, update, or delete collections. |
| `semifluid_schema` | Mutating | `collections:read`, `fields:write`, `views:write` | Create, update, delete, or reorder fields and collection views. |
| `semifluid_records` | Mutating | `records:read`, `records:write` | List, query, aggregate, create, update, upsert, import, or delete records. |
| `semifluid_attachments` | Mutating | `attachments:read`, `attachments:write` | Upload attachments or retrieve authorized attachment metadata/content. |
| `semifluid_suggestions` | Mutating | `records:read`, `records:write` | List, create, inspect, approve, or reject record suggestions. |

## Review Notes

- `search` and `fetch` are the standard read-only knowledge tools for company knowledge and deep
  research style flows.
- Mutating tools must keep accurate `readOnlyHint`, `destructiveHint`, `openWorldHint`, and
  `idempotentHint` annotations on the MCP server.
- Public submission should be tested with realistic prompts for every exposed tool, including
  write-operation confirmation behavior.
- This package does not include screenshots because there is no ChatGPT UI component yet.

## Validation

Minimum validation before submitting or handing off:

```bash
curl https://api.semifluid.ai/.well-known/oauth-protected-resource
```

```bash
curl https://api.semifluid.ai/mcp \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' \
  -H 'Mcp-Protocol-Version: 2025-03-26' \
  --data '{"jsonrpc":"2.0","id":"tools-list","method":"tools/list"}'
```

Then validate in ChatGPT Developer Mode with the prompts in `golden-prompts.md`.
