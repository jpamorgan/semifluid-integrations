---
name: semifluid
description: Use when the user wants to search, inspect, summarize, create, update, delete, or otherwise manage Semifluid collections, schemas, records, attachments, events, intake forms, webhooks, or record suggestions.
---

# Semifluid

Use this skill for Semifluid knowledge retrieval and data operations. For authenticated plugin
work, use the Semifluid MCP tools exposed by Codex. The bundled HTTP helper is available for public
endpoints and explicit compatibility credentials only.

## Core Rule

Use Semifluid MCP tools first for authenticated Semifluid work:

- `search` and `fetch` for high-level retrieval.
- `semifluid_collections` for collection operations.
- `semifluid_records` for record list/query/aggregate/create/update/upsert/import/delete.
- `semifluid_schema` for field and view operations.
- `semifluid_attachments` for attachment operations.
- `semifluid_suggestions` for record suggestion operations.

Use `operationId: "DescribeOperations"` on the relevant grouped tool when an operation name or
payload shape is unclear.

Do not ask the user for an API key in chat. Direct shell API calls require a caller-supplied bearer
token in `SEMIFLUID_ACCESS_TOKEN`, `SEMIFLUID_OAUTH_TOKEN`, or `CODEX_SEMIFLUID_ACCESS_TOKEN`, or
explicit compatibility API-key auth with `SEMIFLUID_API_KEY --auth-header x-api-key`. Codex MCP
OAuth does not expose plugin access tokens to shell subprocesses.

## Quick Start

For public endpoints or explicit compatibility credentials, run commands from this skill directory
or pass the absolute script path:

```bash
python3 scripts/semifluid_api.py health
python3 scripts/semifluid_api.py operations
SEMIFLUID_ACCESS_TOKEN=... python3 scripts/semifluid_api.py get /v1/collections
SEMIFLUID_API_KEY=... python3 scripts/semifluid_api.py get /v1/collections --auth-header x-api-key
```

Use `--json @file.json` for request bodies that are too large or sensitive for the command line.

## Fast Path

For common authenticated operations, use the grouped Semifluid MCP tools directly. Do not run
`DescribeOperations` unless the operation ID or payload shape is unclear, the request fails with a
schema error, or the user asks for an uncommon endpoint.

Expected efficient paths:

- Health check or public spec: one helper command.
- List collections: `semifluid_collections` with `operationId: "ListCollections"`.
- Show records from a known collection: `semifluid_records` with `operationId: "ListCollectionRecords"`.
- Find a collection by name, then read records: `search`, then `fetch` or the relevant grouped tool.
- Query records: `semifluid_records` with `operationId: "QueryCollectionRecords"`.
- Upload an attachment: `semifluid_attachments` with `operationId: "UploadAttachment"`.
- Import CSV records: `semifluid_records` with `operationId: "ImportCollectionRecordsCsv"`.
- Simple record/field/collection write: make the smallest read-only request needed to identify the target, write through the relevant grouped tool, then report the result.

## Workflow

1. Classify the request.
   - Discovery/search: use `search`, `fetch`, or the relevant grouped tool.
   - Details, summaries, or answers: fetch exact collection/record data before answering.
   - Direct collection/schema/record/attachment/suggestion operation: use the narrowest matching grouped tool operation.
2. Discover schemas only when needed.
   - Use `DescribeOperations` for unfamiliar operation shapes.
   - Read `references/api-reference.md` or run `python3 scripts/semifluid_api.py spec` only when the grouped tool reference is insufficient.
3. Ground answers in returned API data.
   - Do not claim exact details from memory or a guessed schema.
   - Summarize Semifluid content concisely and mention the collection, record, or endpoint when useful.
4. Handle errors directly.
   - For validation errors, adjust the payload from the endpoint schema or ask for missing required values.
   - For MCP auth/session errors, tell the user to reconnect or reauthorize the Semifluid plugin and retry in a new thread.
   - For helper missing-token errors, explain that Codex MCP OAuth does not expose plugin access tokens to shell subprocesses.

## Mutation Rules

- Mutations require the relevant OAuth scopes and the user's Semifluid permissions.
- For create/update/upsert/import/reorder/review operations, make sure the target collection,
  field, record, attachment, suggestion, and payload are clear before calling the grouped tool.
- For delete operations, confirm the exact destructive action unless the user has explicitly asked
  for that specific delete in the current turn.
- Prefer direct record operations when the user asks you to make a change now.
- Prefer suggestion endpoints when the user asks you to propose, stage, or request review of a
  change instead of applying it directly.
- Report status codes and concise results. Do not include secrets in outputs.

## Helper Notes

- The helper uses only Python standard library modules.
- Authenticated helper requests send `Authorization: Bearer <token>` by default when a bearer token
  environment variable is explicitly set.
- Set `SEMIFLUID_API_TRACE=/path/to/trace.jsonl` or pass `--trace-output /path/to/trace.jsonl` to append machine-readable request timing events.
- Trace events never include OAuth tokens, API keys, request bodies, response bodies, or query values.
- Use `--no-auth` only for public endpoints such as `/v1/health`.
- Use `--base-url` if targeting a non-production Semifluid API.
- Use `--output path` for large responses or files.

## Safety And Auth

- Never ask the user for an API key in chat.
- Never print or store credentials.
- If the helper reports a missing bearer token, use Semifluid MCP tools for normal authenticated
  plugin work.
- If Semifluid MCP tools report `Auth required`, tell the user to reconnect or reauthorize the
  Semifluid plugin and retry in a new thread.
