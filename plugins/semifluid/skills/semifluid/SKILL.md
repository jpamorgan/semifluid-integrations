---
name: semifluid
description: Use when the user wants to search, inspect, summarize, or answer questions from Semifluid collections and records through the Semifluid MCP tools. The Semifluid MCP is read-only.
---

# Semifluid

Use this skill for Semifluid knowledge retrieval. Semifluid access is provided by the bundled MCP
server, not by direct REST calls.

## Core Rule

Use the Semifluid MCP tools first and only:

- `mcp__semifluid.search`
- `mcp__semifluid.fetch`

Do not use curl, OpenAPI specs, old `/tables` or `/v1` REST endpoints, local API helper scripts, or
hand-written HTTP requests for Semifluid work.

If the Semifluid MCP tools are not visible in the active tool list, use `tool_search` with a query
such as `semifluid collections records MCP tools` to load them. If they still are not available,
tell the user that the Semifluid MCP plugin needs to be enabled or the thread needs to be restarted
after plugin installation.

## Tool Contract

`mcp__semifluid.search({ "query": "..." })`

- Use to find Semifluid collections by name and records by content.
- Search with the user's own terms first.
- Prefer one focused search over several broad searches.
- If the first search misses, retry with synonyms, shorter nouns, or exact names from the user's
  request.

`mcp__semifluid.fetch({ "id": "..." })`

- Use when a search result is relevant and the user needs details, exact content, or a grounded
  answer.
- The `id` must come from `search` results, such as `collection:<id>` or `record:<id>`.
- Fetch only the relevant result IDs. Do not bulk-fetch everything unless the user explicitly asks
  for exhaustive review.

The MCP tools are read-only. They can search and fetch collections and records, but they cannot
create, update, delete, import, upload attachments, manage API keys, or change schema.

## Workflow

1. Classify the request.
   - Search/discovery: use `search`.
   - Details, summaries, or answers about a result: use `search`, then `fetch` the relevant IDs.
   - Mutation requests: explain that the current Semifluid MCP is read-only and cannot perform the
     change.
2. Keep queries tight.
   - Use names, titles, people, projects, keywords, or phrases from the user's request.
   - For ambiguous requests, run a small search first and use the result titles to narrow the next
     step.
3. Ground answers in fetched content.
   - Do not claim exact details from a search snippet alone when a fetched record is needed.
   - Summarize Semifluid content concisely and mention which collection or record the answer came
     from when useful.
4. Handle no-result cases directly.
   - Say that the MCP search returned no matching Semifluid results.
   - Offer the closest next search terms only when they are obvious from the user's wording.

## Common Patterns

Find a collection:

1. `mcp__semifluid.search({ "query": "<collection name or topic>" })`
2. Fetch the `collection:<id>` result if the user needs the full collection text or fields.

Find records in a collection or topic:

1. Search for the collection name plus the record keywords.
2. Fetch the most relevant `record:<id>` results.
3. Answer from the fetched content, not from memory.

Answer a factual question from Semifluid:

1. Search for the key entities in the question.
2. Fetch the best matching records.
3. If fetched content is insufficient, say what was found and what remains unknown.

## Safety And Auth

- Never ask the user for an API key in chat.
- Never print or store credentials.
- If the MCP reports an authentication/session error, tell the user to authenticate or reconnect the
  Semifluid plugin, then retry in a new thread if needed.
- Do not fall back to direct HTTP requests after MCP auth or search failures.
