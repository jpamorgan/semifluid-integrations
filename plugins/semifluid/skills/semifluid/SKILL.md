---
name: semifluid
description: Use when the user wants to search, inspect, summarize, create, update, delete, or otherwise manage Semifluid collections, schemas, records, attachments, events, intake forms, webhooks, or record suggestions through the Semifluid HTTP API.
---

# Semifluid

Use this skill for Semifluid knowledge retrieval and data operations. Operate through the bundled
Semifluid HTTP API helper, not through Semifluid MCP tools.

## Core Rule

Use `scripts/semifluid_api.py` first for Semifluid work:

```bash
python3 scripts/semifluid_api.py health
python3 scripts/semifluid_api.py operations
python3 scripts/semifluid_api.py get /v1/collections
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=10 --query fields='*'
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/records/query --json '{"limit":10,"search":"search text","fields":"*"}'
```

The helper uses OAuth bearer auth by default. If no token is cached yet, authorize the helper once:

```bash
python3 scripts/semifluid_api.py auth login
python3 scripts/semifluid_api.py auth status
```

The helper caches OAuth credentials locally and refreshes access tokens when possible. It also
accepts explicit bearer token overrides from `SEMIFLUID_ACCESS_TOKEN`, `SEMIFLUID_OAUTH_TOKEN`, or
`CODEX_SEMIFLUID_ACCESS_TOKEN`.

Do not use Semifluid MCP tools for normal Semifluid operations. Do not ask the user for an API key
in chat. API-key auth exists only as an explicit compatibility mode in the helper.

## Quick Start

Run commands from this skill directory or pass the absolute script path:

```bash
python3 scripts/semifluid_api.py health
python3 scripts/semifluid_api.py auth login
python3 scripts/semifluid_api.py operations
python3 scripts/semifluid_api.py get /v1/collections
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=10 --query fields='*'
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/records/query --json @query.json
python3 scripts/semifluid_api.py post /v1/attachments --json @attachment.json
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/record-imports --json @csv-import.json
python3 scripts/semifluid_api.py get /v1/events --query limit=10 --query direction=desc
python3 scripts/semifluid_api.py get /v1/intake-forms --query collectionId={collectionId}
python3 scripts/semifluid_api.py get /v1/webhooks
```

Use `--json @file.json` for request bodies that are too large or sensitive for the command line.

## Fast Path

For common operations shown here or in `references/api-reference.md`, call
`scripts/semifluid_api.py` directly. Do not fetch the live spec or run `operations` unless the
endpoint/body shape is unclear, the request fails with a schema error, or the user asks for an
uncommon endpoint.

Expected efficient paths:

- Health check: one `health` command.
- List collections: one `get /v1/collections` command.
- Show records from a known collection: one `get /v1/collections/{collectionId}/records --query limit=N --query fields='*'` command.
- Find a collection by name, then read records: `get /v1/collections`, then one records command.
- Query records: one `post /v1/collections/{collectionId}/records/query --json @query.json` command.
- Upload an attachment: one `post /v1/attachments --json @attachment.json` command after building a request body with `collectionId`, `name`, optional `mimeType`, and `dataBase64`.
- Import CSV records: one `post /v1/collections/{collectionId}/record-imports --json @csv-import.json` command after building a request body with `csv`, optional `headerRow`, optional `columns`, and optional `validateOnly`.
- List events: one `get /v1/events --query limit=N --query direction=desc` command; add `--query collectionId=...` for a collection-scoped list.
- List webhooks: one `get /v1/webhooks` command; add `--query collectionId=...` for a collection-scoped list.
- Simple record/field/collection write: make the smallest read-only request needed to identify the target, write with `--json @file.json`, then report the result.

## Workflow

1. Classify the request.
   - Discovery/search: list or query the relevant collections/records endpoint.
   - Details, summaries, or answers: fetch exact collection/record data before answering.
   - Direct collection/schema/record/attachment/suggestion operation: use the narrowest matching API endpoint.
2. Discover schemas only when needed.
   - Read `references/api-reference.md` for unfamiliar endpoint shapes.
   - Run `python3 scripts/semifluid_api.py spec` only when the local reference is insufficient.
3. Ground answers in returned API data.
   - Do not claim exact details from memory or a guessed schema.
   - Summarize Semifluid content concisely and mention the collection, record, or endpoint when useful.
4. Handle errors directly.
   - For validation errors, adjust the payload from the endpoint schema or ask for missing required values.
   - For missing local OAuth credentials, run `python3 scripts/semifluid_api.py auth login`.
   - For invalid or expired cached OAuth credentials, run `python3 scripts/semifluid_api.py auth login` again.

## Mutation Rules

- Mutations require the relevant OAuth scopes and the user's Semifluid permissions.
- For create/update/upsert/import/reorder/review operations, make sure the target collection,
  field, record, attachment, suggestion, and payload are clear before calling the helper.
- For delete operations, confirm the exact destructive action unless the user has explicitly asked
  for that specific delete in the current turn.
- Prefer direct record operations when the user asks you to make a change now.
- Prefer suggestion endpoints when the user asks you to propose, stage, or request review of a
  change instead of applying it directly.
- Report status codes and concise results. Do not include secrets in outputs.

## Helper Notes

- The helper uses only Python standard library modules.
- Authenticated requests send `Authorization: Bearer <token>` by default.
- Run `python3 scripts/semifluid_api.py auth login` to create the local OAuth cache used by API calls.
- Run `python3 scripts/semifluid_api.py auth logout` to remove cached OAuth credentials.
- Set `SEMIFLUID_API_TRACE=/path/to/trace.jsonl` or pass `--trace-output /path/to/trace.jsonl` to append machine-readable request timing events.
- Trace events never include OAuth tokens, API keys, request bodies, response bodies, or query values.
- Use `--no-auth` only for public endpoints such as `/v1/health`.
- Use `--base-url` if targeting a non-production Semifluid API.
- Use `--output path` for large responses or files.

## Safety And Auth

- Never ask the user for an API key in chat.
- Never print or store credentials.
- If the helper reports a missing OAuth token, run `python3 scripts/semifluid_api.py auth login`.
- Do not fall back to MCP tools after API auth, validation, or search failures.
