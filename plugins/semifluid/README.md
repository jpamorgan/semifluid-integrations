# Semifluid Codex Plugin

This is the installable Codex plugin bundle for Semifluid.

## Contents

- `.codex-plugin/plugin.json`: required Codex plugin manifest.
- `.mcp.json`: bundled MCP server config for `https://api.semifluid.ai/mcp`.
- `skills/semifluid/SKILL.md`: Codex guidance for Semifluid retrieval and mutations.

## Install

Install this plugin through the repository marketplace from the repository root:

```bash
codex plugin marketplace add /Users/jpamorgan/Development/semifluid-integrations
```

Or from GitHub:

```bash
codex plugin marketplace add jpamorgan/semifluid-integrations
```

Then open Codex, choose the `Semifluid Integrations` marketplace, install `Semifluid`, and start a
new thread.

## MCP Server

The bundled MCP server is remote and OAuth-protected:

```text
https://api.semifluid.ai/mcp
```

Codex should use the tools exposed by that server instead of direct REST calls.

## Plugin Authoring Notes

- The folder name, manifest `name`, marketplace plugin entry, and skill namespace should stay
  aligned as `semifluid`.
- Keep bundled plugin files at the plugin root, except for `.codex-plugin/plugin.json`.
- Keep `.mcp.json` in the `mcpServers` companion shape validated by the local Codex plugin tooling.
- Keep starter prompts short and limit them to the first three useful examples.
- Restart Codex and test in a fresh thread after changing manifest, skill, or MCP config files.
