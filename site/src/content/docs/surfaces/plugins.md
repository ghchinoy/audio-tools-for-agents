---
title: Agent Plugins Specification
description: Conformance with Agent Plugins Spec v1.0.0 and marketplace indexing.
---

`audio-tools-for-agents` conforms strictly to the [Agent Plugins Specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec).

## Root Manifest (`plugin.json`)

The package manifest resides at the repository root and adheres to the closed schema defined in Specification §5:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "audio-tools",
  "version": "0.1.0",
  "description": "Deterministic audio manipulation tools and deep learning stems separation for AI agents.",
  "author": {
    "name": "G. H. Chinoy"
  },
  "license": "Apache-2.0",
  "keywords": [
    "audio",
    "stems",
    "demucs",
    "htdemucs",
    "music",
    "mcp",
    "agent-skill"
  ]
}
```

## Marketplace Index (`.claude-plugin/marketplace.json`)

To enable multi-plugin repository discovery, the marketplace manifest registers the plugin and its associated skills:

```json
{
  "name": "audio-tools-for-agents",
  "metadata": {
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "audio-stemming",
      "source": "./plugins/audio-stemming",
      "description": "Deterministic audio stem separation using Meta HTDemucs deep learning models.",
      "skills": [
        "./plugins/audio-stemming/skills/audio-stemming"
      ]
    }
  ]
}
```

## Verification

To verify that manifests and skill structures comply with all normative rules:

```bash
make validate-spec
```
