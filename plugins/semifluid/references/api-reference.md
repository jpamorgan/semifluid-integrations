# Semifluid API Reference

Source: `https://api.semifluid.ai/api-reference/spec.json`

Last refreshed from source: `2026-06-27`

OpenAPI: `3.1.1`

API version: `0.1.198`

Base URL: `https://api.semifluid.ai`

JSON spec: `https://api.semifluid.ai/api-reference/spec.json`

YAML spec: `https://api.semifluid.ai/api-reference/spec.yaml`

Auth: the plugin helper sends OAuth bearer credentials as `Authorization: Bearer <token>` by
default. API-key auth is available only as an explicit compatibility mode with
`--auth-header x-api-key`.

The helper reports each API request duration to stderr as `Timing: METHOD /path -> HTTP status in N.N ms`, while response bodies remain on stdout.

## Current Naming

The current public API uses `/v1/...` paths and `records` terminology. Older docs, examples, or code may use unversioned paths, `rows`, `rowId`, `tables`, or collection-scoped attachment/suggestion routes; prefer `/v1`, `records`, `recordId`, `collections`, and the endpoint paths below.

Use `key` for client-defined record keys. Use `recordId` only for Semifluid UUID record identifiers.

## Common Commands

```bash
python3 scripts/semifluid_api.py health
python3 scripts/semifluid_api.py operations
python3 scripts/semifluid_api.py get /v1/collections
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}
python3 scripts/semifluid_api.py get /v1/collections/{collectionId}/records --query limit=50 --query fields='*'
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/records/query --json @query.json
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/record-aggregations --json @aggregate.json
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/records --json @records-create.json
python3 scripts/semifluid_api.py patch /v1/collections/{collectionId}/records --json @records-update.json
python3 scripts/semifluid_api.py put /v1/collections/{collectionId}/records --json @records-upsert.json
python3 scripts/semifluid_api.py post /v1/attachments --json @attachment.json
python3 scripts/semifluid_api.py post /v1/collections/{collectionId}/record-imports --json @csv-import.json
python3 scripts/semifluid_api.py get /v1/events --query limit=10 --query direction=desc
python3 scripts/semifluid_api.py get /v1/intake-forms --query collectionId={collectionId}
python3 scripts/semifluid_api.py get /v1/webhooks
python3 scripts/semifluid_api.py post /v1/webhooks --json @webhook.json
```

## Operations

| Method | Path | Operation | Purpose |
| --- | --- | --- | --- |
| GET | `/v1/api-keys` | `ListApiKeys` | List workspace API keys |
| POST | `/v1/api-keys` | `CreateApiKey` | Create workspace API key |
| DELETE | `/v1/api-keys/{apiKeyId}` | `DeleteApiKey` | Delete workspace API key |
| GET | `/v1/api-keys/{apiKeyId}` | `GetApiKey` | Get workspace API key |
| PATCH | `/v1/api-keys/{apiKeyId}` | `UpdateApiKey` | Update workspace API key |
| POST | `/v1/api-keys/{apiKeyId}/secret-rotations` | `CreateApiKeySecretRotation` | Rotate workspace API key secret |
| POST | `/v1/attachments` | `UploadAttachment` | Upload attachment |
| GET | `/v1/attachments/{attachmentId}` | `GetAttachment` | Get attachment metadata |
| GET | `/v1/collections` | `ListCollections` | List collections |
| POST | `/v1/collections` | `CreateCollection` | Create collection |
| DELETE | `/v1/collections/{collectionId}` | `DeleteCollection` | Soft-delete collection |
| GET | `/v1/collections/{collectionId}` | `GetCollectionDefinition` | Get collection |
| PATCH | `/v1/collections/{collectionId}` | `UpdateCollection` | Update collection |
| PATCH | `/v1/collections/{collectionId}/fields` | `UpdateCollectionFields` | Bulk update fields |
| POST | `/v1/collections/{collectionId}/fields` | `CreateCollectionField` | Create field |
| DELETE | `/v1/collections/{collectionId}/fields/{fieldId}` | `DeleteCollectionField` | Soft-delete field |
| PATCH | `/v1/collections/{collectionId}/fields/{fieldId}` | `UpdateCollectionField` | Update field |
| POST | `/v1/collections/{collectionId}/record-aggregations` | `AggregateCollectionRecords` | Aggregate records |
| POST | `/v1/collections/{collectionId}/record-imports` | `ImportCollectionRecordsCsv` | Import records from CSV |
| DELETE | `/v1/collections/{collectionId}/records` | `DeleteCollectionRecords` | Soft-delete records |
| GET | `/v1/collections/{collectionId}/records` | `ListCollectionRecords` | List records |
| PATCH | `/v1/collections/{collectionId}/records` | `UpdateCollectionRecords` | Update records |
| POST | `/v1/collections/{collectionId}/records` | `CreateCollectionRecords` | Create records |
| PUT | `/v1/collections/{collectionId}/records` | `UpsertCollectionRecords` | Upsert records |
| PUT | `/v1/collections/{collectionId}/records/key/{key}` | `UpsertCollectionRecordByKey` | Upsert record by key |
| POST | `/v1/collections/{collectionId}/records/lookup` | `LookupCollectionRecords` | Look up records |
| POST | `/v1/collections/{collectionId}/records/missing-values` | `FindMissingCollectionRecords` | Find records with missing values |
| POST | `/v1/collections/{collectionId}/records/query` | `QueryCollectionRecords` | Query records |
| DELETE | `/v1/collections/{collectionId}/records/{recordId}` | `DeleteCollectionRecord` | Soft-delete record |
| GET | `/v1/collections/{collectionId}/records/{recordId}` | `GetCollectionRecord` | Get record |
| PATCH | `/v1/collections/{collectionId}/records/{recordId}` | `UpdateCollectionRecord` | Update record |
| GET | `/v1/collections/{collectionId}/views` | `ListCollectionViews` | List collection views |
| PATCH | `/v1/collections/{collectionId}/views` | `UpdateCollectionViews` | Bulk update collection views |
| POST | `/v1/collections/{collectionId}/views` | `CreateCollectionView` | Create collection view |
| DELETE | `/v1/collections/{collectionId}/views/{viewId}` | `DeleteCollectionView` | Delete collection view |
| PATCH | `/v1/collections/{collectionId}/views/{viewId}` | `UpdateSavedCollectionView` | Update collection view |
| GET | `/v1/events` | `ListEvents` | List events |
| GET | `/v1/health` | `HealthCheck` | Health check |
| GET | `/v1/intake-forms` | `ListIntakeForms` | List intake forms |
| POST | `/v1/intake-forms` | `CreateIntakeForm` | Create intake form |
| DELETE | `/v1/intake-forms/{intakeFormId}` | `DeleteIntakeForm` | Delete intake form |
| GET | `/v1/intake-forms/{intakeFormId}` | `GetIntakeForm` | Get intake form |
| PATCH | `/v1/intake-forms/{intakeFormId}` | `UpdateIntakeForm` | Update intake form |
| GET | `/v1/public-shares` | `ListPublicShares` | List public shares |
| POST | `/v1/public-shares` | `CreatePublicShare` | Create public share |
| DELETE | `/v1/public-shares/{publicShareId}` | `DeletePublicShare` | Delete public share |
| GET | `/v1/public-shares/{publicShareId}` | `GetPublicShare` | Get public share |
| PATCH | `/v1/public-shares/{publicShareId}` | `UpdatePublicShare` | Update public share |
| GET | `/v1/public/intake-forms/{intakeFormToken}` | `GetPublicIntakeForm` | Get public intake form |
| POST | `/v1/public/intake-forms/{intakeFormToken}/submissions` | `SubmitIntakeForm` | Submit intake form response |
| GET | `/v1/public/shared-collections/{publicShareToken}` | `GetPublicShareCollection` | Get public share collection |
| POST | `/v1/public/shared-collections/{publicShareToken}/record-aggregations` | `AggregatePublicShareRecords` | Aggregate public share records |
| GET | `/v1/public/shared-collections/{publicShareToken}/records` | `ListPublicShareRecords` | List public share records |
| POST | `/v1/public/shared-collections/{publicShareToken}/records/query` | `QueryPublicShareRecords` | Query public share records |
| GET | `/v1/public/shared-collections/{publicShareToken}/records/{recordId}` | `GetPublicShareRecord` | Get public share record |
| GET | `/v1/record-suggestions` | `ListRecordSuggestions` | List suggestions |
| POST | `/v1/record-suggestions` | `CreateRecordSuggestion` | Suggest a record change |
| GET | `/v1/record-suggestions/{suggestionId}` | `GetRecordSuggestion` | Get suggestion |
| POST | `/v1/record-suggestions/{suggestionId}/reviews` | `CreateRecordSuggestionReview` | Review suggestion |
| GET | `/v1/webhooks` | `ListWebhooks` | List workspace webhooks |
| POST | `/v1/webhooks` | `CreateWebhook` | Create webhook |
| DELETE | `/v1/webhooks/{webhookId}` | `DeleteWebhook` | Delete webhook |
| GET | `/v1/webhooks/{webhookId}` | `GetWebhook` | Get webhook |
| PATCH | `/v1/webhooks/{webhookId}` | `UpdateWebhook` | Update webhook |
| GET | `/v1/webhooks/{webhookId}/deliveries` | `ListWebhookDeliveries` | List webhook deliveries |
| POST | `/v1/webhooks/{webhookId}/deliveries` | `CreateWebhookDelivery` | Create webhook delivery |

## Parameters

- All API routes from the spec are versioned under `/v1`. Only `/api-reference/spec.json` and `/api-reference/spec.yaml` are unversioned helper/reference routes.
- UUID path parameters include `collectionId`, `recordId`, `fieldId`, `attachmentId`, `viewId`, `publicShareId`, `intakeFormId`, `suggestionId`, and `webhookId`.
- `apiKeyId` is a non-empty string. `publicShareToken` is a 43-character URL-safe token matching `^[A-Za-z0-9_-]{43}$`; `intakeFormToken` is a public token string from 32 to 256 characters.
- List endpoints generally default `limit` to `50` and cap `limit` at `100`; webhook deliveries default to `20` and cap at `50`.
- Record read and write endpoints support `fields: "*"` or an array of up to 100 field keys. For GET query strings, pass `--query fields='*'`; for POST/PATCH/PUT requests, include `fields` in the JSON body.
- Field keys in record values must match `^[A-Za-z_][A-Za-z0-9_]*$`.
- `POST /v1/attachments` accepts `collectionId`, `name`, optional `mimeType`, and `dataBase64` up to 34,952,536 characters.
- `GET /v1/events` supports `limit`, `cursor`, `includePayload`, `direction=asc|desc`, `collectionId`, `recordId`, `operation`, `entityType`, and `entityId`; `direction` defaults to `asc`.
- `GET /v1/webhooks` accepts optional `collectionId`; `GET /v1/webhooks/{webhookId}/deliveries` accepts optional `limit`.

## API Keys

API key names must be 1 to 64 characters. If `access` is omitted when creating a key, the API creates a workspace-wide key.

Create a workspace-wide key:

```json
{
  "name": "Agent key",
  "access": {
    "kind": "workspace"
  }
}
```

Create a collection-scoped key:

```json
{
  "name": "Readonly collection key",
  "access": {
    "kind": "collection_scoped",
    "grants": [
      {
        "collectionId": "00000000-0000-0000-0000-000000000000",
        "scope": "read_only"
      }
    ]
  }
}
```

Collection-scoped grant scopes: `read_only`, `record_suggester`, `suggestion_reviewer`, `record_editor`, `locked_record_editor`, `collection_admin`.

Collection-scoped grants may include `capabilities`, currently `public_share_manage` and `intake_form_manage`.

Update or rename an API key with `PATCH /v1/api-keys/{apiKeyId}`:

```json
{
  "name": "Collection admin key",
  "access": {
    "kind": "collection_scoped",
    "grants": [
      {
        "collectionId": "00000000-0000-0000-0000-000000000000",
        "scope": "collection_admin",
        "capabilities": ["public_share_manage", "intake_form_manage"]
      }
    ]
  },
  "preset": "collection-admin",
  "reason": "Grant admin access for automation"
}
```

Rotate a key secret with `POST /v1/api-keys/{apiKeyId}/secret-rotations`. The new secret is only returned in the rotation response.

## Collections And Fields

Create a collection:

```json
{
  "name": "Tasks",
  "icon": {
    "type": "emoji",
    "emoji": "T"
  },
  "description": "Task tracker",
  "isLocked": false,
  "fields": [
    {
      "name": "Status",
      "key": "status",
      "type": "select",
      "options": [
        {
          "label": "Open",
          "value": "open"
        }
      ]
    }
  ]
}
```

Collection names are required. Collection descriptions, icons, `isLocked`, and initial `fields` are optional. Initial field lists are capped at 100 fields.

`PATCH /v1/collections/{collectionId}` accepts any subset of `name`, `icon`, `description`, `isLocked`, `projectName`, `visibility`, and `metadata`.

Field create requires `name`, `key`, and `type`; it also accepts optional `description`, `config`, `isRequired`, `isHidden`, `isPrimary`, `position`, and `options`. Field update accepts `name`, `description`, `config`, `isRequired`, `isHidden`, `isPrimary`, and `options`.

Field types from the spec: `text`, `markdown`, `select`, `status`, `multi_select`, `attachment`, `phone`, `number`, `currency`, `auto_number`, `boolean`, `date`, `date_time`, `email`, `url`, `relation`, `lookup`, `rollup`.

Select/status options use `label`, optional `value`, optional `color`, and optional `id` when updating. Option arrays are capped at 100 options, and option values are capped at 128 characters.

Bulk reorder fields with `PATCH /v1/collections/{collectionId}/fields`:

```json
{
  "fieldIds": ["00000000-0000-0000-0000-000000000000"]
}
```

## Records

Create, update, delete, query, aggregate, look up, import, or upsert records. Bulk write batches require 1 to 1000 records. Record keys must be 1 to 191 characters.

Create records with `POST /v1/collections/{collectionId}/records`:

```json
{
  "records": [
    {
      "key": "external-record-key",
      "values": {
        "field_key": "value"
      }
    }
  ],
  "fields": "*",
  "returning": "records",
  "mutationMode": "partial"
}
```

Update records by `recordId` or `key` with `PATCH /v1/collections/{collectionId}/records`:

```json
{
  "records": [
    {
      "recordId": "00000000-0000-0000-0000-000000000000",
      "values": {
        "field_key": "new value"
      },
      "isLocked": false
    }
  ],
  "fields": "*",
  "returning": "records",
  "mutationMode": "partial"
}
```

Delete records with `DELETE /v1/collections/{collectionId}/records`:

```json
{
  "records": [
    {
      "key": "external-record-key"
    }
  ],
  "mutationMode": "all_or_nothing"
}
```

Upsert records with `PUT /v1/collections/{collectionId}/records`:

```json
{
  "records": [
    {
      "key": "external-record-key",
      "values": {
        "field_key": "value"
      }
    }
  ],
  "fields": "*",
  "returning": "records",
  "mutationMode": "partial"
}
```

Upsert one record by key with `PUT /v1/collections/{collectionId}/records/key/{key}`:

```json
{
  "values": {
    "field_key": "value"
  },
  "fields": "*",
  "returning": "records"
}
```

Batch write modes: `partial` attempts each record independently and returns per-item results. `all_or_nothing` applies the whole batch transactionally.

Create/update/upsert calls default to `returning: "ids"` and `fields: []`. Use `returning: "records"` plus `fields: "*"` or a field-key array when the response should include record values.

Use `PATCH /v1/collections/{collectionId}/records/{recordId}` for one-record updates and `DELETE /v1/collections/{collectionId}/records/{recordId}` for one-record deletes.

## Attachments

Upload an attachment before storing it in an attachment field:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "name": "file.pdf",
  "mimeType": "application/pdf",
  "dataBase64": "<base64 file contents>"
}
```

Use `POST /v1/attachments`. Get attachment metadata with `GET /v1/attachments/{attachmentId}`. Attachment field values use arrays of the attachment metadata returned by upload:

```json
{
  "attachment_field": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "name": "file.pdf",
      "mimeType": "application/pdf",
      "size": 12345,
      "url": "https://api.semifluid.ai/...",
      "createdAt": "2026-06-18T00:00:00.000Z"
    }
  ]
}
```

## Query Records

Use `POST /v1/collections/{collectionId}/records/query` for body-based query, filtering, search, sorting, and projection:

```json
{
  "limit": 50,
  "cursor": "next-cursor",
  "search": "search text",
  "fields": "*",
  "filters": [
    {
      "field": "status",
      "operator": "eq",
      "value": "Open"
    }
  ],
  "filterMode": "all",
  "sort": [
    {
      "field": "createdAt",
      "direction": "desc"
    }
  ]
}
```

Filter operators: `eq`, `neq`, `is_empty`, `is_not_empty`, `gt`, `gte`, `lt`, `lte`, `contains`, `starts_with`, `in`, `not_in`, `between`.

Query limits: `limit` is 1-100, `search` is at most 256 characters, filters are capped at 25, sort entries are capped at 10, and explicit `fields` arrays are capped at 100 field keys.

`search` performs case-insensitive broad record search over searchable text-like values, including text, markdown, email, phone, URL, select/status labels, multi-select labels, and attachment file names.

Look up records by ID with `POST /v1/collections/{collectionId}/records/lookup`:

```json
{
  "recordIds": ["00000000-0000-0000-0000-000000000000"],
  "fields": "*"
}
```

## Aggregate Records

Use `POST /v1/collections/{collectionId}/record-aggregations`:

```json
{
  "search": "search text",
  "filters": [
    {
      "field": "status",
      "operator": "eq",
      "value": "Open"
    }
  ],
  "filterMode": "all",
  "metrics": [
    {
      "key": "count",
      "operation": "count"
    },
    {
      "key": "total",
      "operation": "sum",
      "field": "amount"
    }
  ],
  "groupBy": {
    "field": "createdAt",
    "dateBucket": "month"
  },
  "sort": {
    "metric": "total",
    "direction": "desc"
  },
  "limit": 100
}
```

Aggregate metric operations: `count`, `count_values`, `count_empty`, `count_unique`, `count_true`, `count_false`, `count_items`, `count_unique_items`, `sum`, `avg`, `min`, `max`.

Aggregate requests default to one metric: `{ "key": "count", "operation": "count" }`. Requests accept 1 to 10 metrics. Metric keys must be 1 to 128 characters and match `^[A-Za-z0-9][A-Za-z0-9_.:-]*$`.

`countLimit` can cap count-like ungrouped metrics from 1 to 1,000,000. Date buckets: `day`, `week`, `month`, `year`. Week buckets start on Monday and date buckets use UTC.

## Missing Values

Use `POST /v1/collections/{collectionId}/records/missing-values`:

```json
{
  "fields": ["summary", "owner"],
  "contextFields": ["name"],
  "matchMode": "any",
  "limit": 50
}
```

Use `fields: "*"` to inspect all fields. Missing match modes: `any`, `all`.

## CSV Imports

Import CSV rows with `POST /v1/collections/{collectionId}/record-imports`:

```json
{
  "csv": "name,status\nFirst task,Open\n",
  "headerRow": true,
  "columns": ["name", "status"],
  "validateOnly": false
}
```

CSV imports are atomic: if any cell fails validation, no records are created. Requests accept at most 1000 data rows, raw CSV text up to 5,242,880 characters, and up to 200 explicit column mappings. If `columns` is omitted, `headerRow` must be true and headers are auto-mapped to fields by key or name case-insensitively. Use `null` in `columns` to skip a CSV column.

## Suggestions

Suggestions let a caller propose record creates, updates, or deletes for later review. Use `POST /v1/record-suggestions`.

Suggest a new record:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "kind": "create",
  "values": {
    "name": "New task",
    "status": "Open"
  },
  "note": "Suggested by import review"
}
```

Suggest an update:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "kind": "update",
  "recordId": "00000000-0000-0000-0000-000000000000",
  "values": {
    "status": "Done"
  },
  "note": "Status should match source system"
}
```

Suggest a delete:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "kind": "delete",
  "recordId": "00000000-0000-0000-0000-000000000000",
  "note": "Duplicate record"
}
```

List suggestions with `GET /v1/record-suggestions --query collectionId=...`. Optional query parameters include `limit`, `cursor`, and `status=pending|approved|rejected`.

Review a suggestion with `POST /v1/record-suggestions/{suggestionId}/reviews`:

```json
{
  "status": "approved",
  "note": "Reviewed and accepted"
}
```

## Intake Forms

Manage forms with workspace-authenticated endpoints:

- `GET /v1/intake-forms --query collectionId=...`
- `POST /v1/intake-forms`
- `GET /v1/intake-forms/{intakeFormId}`
- `PATCH /v1/intake-forms/{intakeFormId}`
- `DELETE /v1/intake-forms/{intakeFormId}`

Create an intake form:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "title": "Task intake",
  "description": "Submit a task request",
  "successMessage": "Thanks",
  "isEnabled": true,
  "fields": [
    {
      "fieldId": "00000000-0000-0000-0000-000000000000",
      "required": true,
      "label": "Task name",
      "helpText": "Use a short descriptive title"
    }
  ]
}
```

Create requires `collectionId`, `title`, and at least one field. Title is capped at 120 characters, description at 2000, success message at 1000, and form field lists at 50 fields. Field labels are capped at 120 characters and help text at 500.

Public form endpoints use a token and do not require authenticated workspace auth:

```bash
python3 scripts/semifluid_api.py get /v1/public/intake-forms/{intakeFormToken} --no-auth
python3 scripts/semifluid_api.py post /v1/public/intake-forms/{intakeFormToken}/submissions --json @submission.json --no-auth
```

Submit a form:

```json
{
  "values": {
    "name": "New request",
    "status": "Open"
  }
}
```

Submission values are keyed by public field keys. Attachment fields use attachment metadata arrays.

## Saved Views

Create a saved view with `POST /v1/collections/{collectionId}/views`:

```json
{
  "name": "Open tasks",
  "type": "table",
  "config": {}
}
```

Saved view create accepts an optional body and defaults to `name: "Table"` and `type: "table"` when omitted. Saved view names must be 1 to 120 characters. View types: `table`, `grid`, `board`, `map`, `calendar`, `list`, `form`, `dashboard`.

Reorder saved views with `PATCH /v1/collections/{collectionId}/views`:

```json
{
  "viewIds": ["00000000-0000-0000-0000-000000000000"]
}
```

Saved view reorder accepts 1 to 25 view IDs.

Update a saved view with `PATCH /v1/collections/{collectionId}/views/{viewId}`:

```json
{
  "name": "Open tasks",
  "config": {},
  "collectionView": {
    "filters": [
      {
        "field": "status",
        "operator": "eq",
        "value": "Open"
      }
    ],
    "filterMode": "all"
  }
}
```

Collection-view filters are capped at 25, sort entries at 10, field order and hidden field IDs at 100, and field widths at 96 to 1600 pixels.

## Public Shares

Public share management endpoints use authenticated workspace bearer auth:

- `GET /v1/public-shares --query collectionId=...`
- `POST /v1/public-shares`
- `GET /v1/public-shares/{publicShareId}`
- `PATCH /v1/public-shares/{publicShareId}`
- `DELETE /v1/public-shares/{publicShareId}`

Create or replace a public share:

```json
{
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "publicShareToken": "optional-43-character-url-safe-token"
}
```

Public share read endpoints use a `publicShareToken` and do not require workspace credentials when the share is enabled:

- `GET /v1/public/shared-collections/{publicShareToken}`
- `GET /v1/public/shared-collections/{publicShareToken}/records`
- `GET /v1/public/shared-collections/{publicShareToken}/records/{recordId}`
- `POST /v1/public/shared-collections/{publicShareToken}/records/query`
- `POST /v1/public/shared-collections/{publicShareToken}/record-aggregations`

When using the helper for public read endpoints, pass `--no-auth` unless the user explicitly wants to send workspace credentials. Public share record query and aggregation request bodies match the authenticated collection record query and aggregation bodies.

## Webhooks

Webhook endpoints use authenticated workspace bearer auth. Treat webhook secrets and delivery payloads as sensitive; do not include them in final answers, logs, or files unless the user explicitly asks and the destination is appropriate. `POST /v1/webhooks` returns the webhook `secret` only in the create response.

List all webhooks, or filter by collection:

```bash
python3 scripts/semifluid_api.py get /v1/webhooks
python3 scripts/semifluid_api.py get /v1/webhooks --query collectionId=00000000-0000-0000-0000-000000000000
```

Create a webhook:

```json
{
  "name": "Sync listener",
  "url": "https://example.com/semifluid/webhook",
  "collectionId": "00000000-0000-0000-0000-000000000000",
  "events": ["record.created", "record.updated"]
}
```

Create requires `name` and `url`. `name` is 1 to 64 characters, `url` is 1 to 2048 characters, `collectionId` is optional, and `events` is optional but must contain 1 to 9 event types when supplied.

Webhook event types:

- `record.created`, `record.updated`, `record.deleted`
- `field.created`, `field.updated`, `field.deleted`
- `collection.created`, `collection.updated`, `collection.deleted`

Update a webhook:

```json
{
  "name": "Sync listener",
  "url": "https://example.com/semifluid/webhook",
  "collectionId": null,
  "events": ["record.created"],
  "isActive": true
}
```

Update accepts any subset of `name`, `url`, `collectionId`, `events`, and `isActive`. Set `collectionId` to `null` to make the webhook workspace-wide.

Delete a webhook with `DELETE /v1/webhooks/{webhookId}`.

Send a test event:

```bash
python3 scripts/semifluid_api.py post /v1/webhooks/{webhookId}/deliveries --json '{"kind":"test"}'
```

List recent deliveries:

```bash
python3 scripts/semifluid_api.py get /v1/webhooks/{webhookId}/deliveries --query limit=20
```

Webhook delivery results include `eventType`, `status` (`success` or `failed`), `attempts`, `responseStatus`, `errorMessage`, `durationMs`, `payload`, and `createdAt`.

## Events

List workspace or collection events with `GET /v1/events`:

```bash
python3 scripts/semifluid_api.py get /v1/events --query limit=50 --query direction=desc --query includePayload=false
```

Query parameters: `limit`, `cursor`, `includePayload`, `direction=asc|desc`, `collectionId`, `recordId`, `operation`, `entityType`, and `entityId`.

For exact schemas, run:

```bash
python3 scripts/semifluid_api.py spec --output /tmp/semifluid-spec.json
```
