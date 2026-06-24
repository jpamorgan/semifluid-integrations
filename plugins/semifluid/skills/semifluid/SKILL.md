---
name: semifluid
description: Use when the user wants to search, inspect, summarize, create, update, delete, or otherwise manage Semifluid collections, schemas, records, attachments, and record suggestions through the Semifluid MCP tools.
---

# Semifluid

Use this skill for Semifluid knowledge retrieval and data operations. Semifluid access is provided
by the bundled MCP server, not by direct REST calls.

## Core Rule

Use the Semifluid MCP tools first and only:

- `mcp__semifluid.search`
- `mcp__semifluid.fetch`
- `mcp__semifluid.semifluid_collections`
- `mcp__semifluid.semifluid_schema`
- `mcp__semifluid.semifluid_records`
- `mcp__semifluid.semifluid_attachments`
- `mcp__semifluid.semifluid_suggestions`

Do not use curl, OpenAPI specs, old `/tables` or `/v1` REST endpoints, local API helper scripts, or
hand-written HTTP requests for Semifluid work.

If the Semifluid MCP tools are not visible in the active tool list, use `tool_search` with a query
such as `semifluid collections records MCP tools` to load them. If they still are not available,
tell the user that the Semifluid MCP plugin needs to be enabled or the thread needs to be restarted
after plugin installation.

## Tool Selection

Use `search` and `fetch` for retrieval:

- `search`: find collections by name and records by content.
- `fetch`: fetch full text for a `collection:<id>` or `record:<id>` result returned by `search`.

Use grouped tools for direct data API operations:

| Tool | Use for | OAuth scopes |
| --- | --- | --- |
| `semifluid_collections` | List, create, inspect, update, or delete collections. | `collections:read`, `collections:write` |
| `semifluid_schema` | Create, update, delete, or reorder fields and collection views. | `collections:read`, `fields:write`, `views:write` |
| `semifluid_records` | List, query, aggregate, create, update, upsert, import, or delete records. | `records:read`, `records:write` |
| `semifluid_attachments` | Upload attachments or retrieve authorized attachment metadata/content. | `attachments:read`, `attachments:write` |
| `semifluid_suggestions` | List, create, inspect, approve, or reject record suggestions. | `records:read`, `records:write` |

Grouped tools share this input shape:

```json
{
  "operationId": "DescribeOperations",
  "input": {}
}
```

Use `DescribeOperations` on the relevant grouped tool whenever you need exact input schema,
required scopes, path/method, or destructive/read-only flags. Then call the selected operation:

```json
{
  "operationId": "QueryCollectionRecords",
  "input": {
    "collectionId": "<collection-id>"
  }
}
```

## Retrieval Contract

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

## Grouped Operation IDs

`semifluid_collections`

- `ListCollections`
- `CreateCollection`
- `GetCollectionDefinition`
- `UpdateCollection`
- `DeleteCollection`

`semifluid_schema`

- `CreateCollectionField`
- `UpdateCollectionField`
- `DeleteCollectionField`
- `UpdateCollectionFields`
- `ListCollectionViews`
- `CreateCollectionView`
- `UpdateSavedCollectionView`
- `DeleteCollectionView`
- `UpdateCollectionViews`

`semifluid_records`

- `ListCollectionRecords`
- `QueryCollectionRecords`
- `LookupCollectionRecords`
- `FindMissingCollectionRecords`
- `AggregateCollectionRecords`
- `GetCollectionRecord`
- `CreateCollectionRecords`
- `UpdateCollectionRecords`
- `UpdateCollectionRecord`
- `UpsertCollectionRecords`
- `UpsertCollectionRecordByKey`
- `ImportCollectionRecordsCsv`
- `DeleteCollectionRecords`
- `DeleteCollectionRecord`

`semifluid_attachments`

- `UploadAttachment`
- `GetAttachment`
- `GetAttachmentContent`

`semifluid_suggestions`

- `ListRecordSuggestions`
- `CreateRecordSuggestion`
- `GetRecordSuggestion`
- `CreateRecordSuggestionReview`

## Mutation Rules

- Mutating tools require the relevant OAuth scopes and the user's Semifluid permissions.
- For create/update/upsert/import/reorder/review operations, make sure the target collection,
  field, record, attachment, suggestion, and payload are clear before calling the tool.
- For delete operations, confirm the exact destructive action unless the user has explicitly asked
  for that specific delete in the current turn.
- Prefer direct record operations when the user asks you to make a change now.
- Prefer `CreateRecordSuggestion` when the user asks you to propose, stage, or request review of a
  change instead of applying it directly.
- If a mutation fails with missing OAuth scopes, tell the user which scope is missing and ask them
  to reconnect or reauthorize the Semifluid plugin.

## Workflow

1. Classify the request.
   - Search/discovery: use `search`.
   - Details, summaries, or answers about a result: use `search`, then `fetch` relevant IDs.
   - Direct collection/schema/record/attachment/suggestion operation: use the matching grouped tool.
2. Discover schemas when needed.
   - Call `DescribeOperations` before using an unfamiliar operation or when the input shape is not
     obvious.
   - Use the returned input schema instead of guessing field names.
3. Ground answers in fetched or returned content.
   - Do not claim exact details from a search snippet alone when fetched content or an operation
     result is needed.
   - Summarize Semifluid content concisely and mention which collection, record, or operation the
     answer came from when useful.
4. Handle no-result and error cases directly.
   - Say when search returned no matching Semifluid results.
   - For validation errors, adjust the input from the schema or ask the user for missing required
     values.
   - For auth/session errors, tell the user to authenticate or reconnect the Semifluid plugin.

## Common Patterns

Find a collection:

1. `mcp__semifluid.search({ "query": "<collection name or topic>" })`
2. Fetch the `collection:<id>` result if the user needs full collection text or fields.
3. Use `semifluid_collections` with `GetCollectionDefinition` if the user needs structured
   collection details for an operation.

Find or answer from records:

1. Search for the collection name plus record keywords.
2. Fetch the most relevant `record:<id>` results for narrative answers.
3. Use `semifluid_records` with `QueryCollectionRecords`, `LookupCollectionRecords`, or
   `GetCollectionRecord` when structured record data is needed.

Mutate records:

1. Identify the collection and records.
2. Call `semifluid_records` with `DescribeOperations` if the required input shape is unclear.
3. Use the narrowest operation: single-record update/delete for one record, bulk operations only
   when the user asks for bulk changes.
4. Report the operation result and any per-record errors.

Change schema:

1. Use `semifluid_collections` with `GetCollectionDefinition` to inspect existing fields if needed.
2. Use `semifluid_schema` for field and view create/update/delete/reorder operations.
3. Confirm destructive field or view deletion before calling delete operations.

## Safety And Auth

- Never ask the user for an API key in chat.
- Never print or store credentials.
- If the MCP reports an authentication/session error, tell the user to authenticate or reconnect the
  Semifluid plugin, then retry in a new thread if needed.
- Do not fall back to direct HTTP requests after MCP auth, validation, or search failures.
