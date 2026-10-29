# VideoScribe Agent Plugin

Local macOS video-to-transcript tools for agents, with durable asynchronous stdio MCP jobs and an accompanying skill. [中文完整指南](README.md).

The [release ZIP](https://github.com/magiconline/videoscribe-agent-plugin/releases) includes the minimal runtime; source clones use the installer below. Both need external tools and a separate model.

Requires Apple Silicon, Python 3, and external tools:

```sh
brew install yt-dlp ffmpeg whisper.cpp node
git clone https://github.com/magiconline/videoscribe-agent-plugin.git
cd videoscribe-agent-plugin
python3 scripts/prepare-runtime.py
```

The installer verifies the pinned GUI release ZIP against `runtime.json`. An installed `/Applications/VideoScribe.app` or `VIDEOSCRIBE_APP_PATH` also works. Install a multilingual whisper.cpp model using the GUI repository's `scripts/download-model.sh`, or set `VIDEOSCRIBE_MODEL_PATH`. Neither tools nor models are bundled. The runtime is ad-hoc signed and not Apple-notarized; Intel releases are unavailable.

Import the plugin folder in a client supporting Agent Plugins. Root `plugin.json`, `mcp.json`, and `skills/` provide the portable baseline; `.codex-plugin/` and `.mcp.json` provide a separate Codex adapter. Client support varies. Alternatively register the absolute path to `bin/videoscribe-mcp` as a stdio MCP command, with no arguments, and load `skills/video-transcript/SKILL.md` separately.

Call `get_capabilities` first. Submit with `submit_video`, poll `get_job`, and only read or export after `completed`. Export `plain`, `timed`, `srt`, or `json`. Downloads read macOS system proxy settings. Source-language transcription is supported; arbitrary translation, OCR, and diarization are not.

See [tool usage](docs/USAGE.md), [privacy](SECURITY.md), and [third-party notices](THIRD_PARTY_NOTICES.md). Tests validate manifests and installer protections; CI does not perform macOS transcription. Original code is [MIT](LICENSE).
