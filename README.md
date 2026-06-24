# Semifluid Integrations

Codex plugin package for Semifluid integrations.

## Contents

- `plugins/semifluid`: Codex plugin bundle.
- `.agents/plugins/marketplace.json`: Local marketplace entry for the Semifluid plugin.

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
- A Codex skill that instructs agents to use the Semifluid MCP search and fetch tools.

The current MCP surface is read-only.
