#!/usr/bin/env python3
"""Validate the portable manifests and skill metadata, without loading a client."""
import json
from pathlib import Path
import jsonschema
import yaml
root = Path(__file__).resolve().parents[1]
for name in ('plugin', 'mcp'):
    document = json.loads((root / f'{name}.json').read_text())
    schema = json.loads((root / 'schemas' / f'{name}.schema.json').read_text())
    jsonschema.validate(document, schema)
text = (root / 'skills/video-transcript/SKILL.md').read_text()
metadata = yaml.safe_load(text.split('---', 2)[1])
assert metadata['name'] == 'video-transcript' and metadata['description']
for relative in ('.codex-plugin/plugin.json', '.mcp.json', '.agents/plugins/marketplace.json', 'runtime.json'):
    json.loads((root / relative).read_text())
assert (root / 'bin/videoscribe-mcp').stat().st_mode & 0o111
print('PASS: portable schemas, skill metadata, adapter JSON, launcher')
