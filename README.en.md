# VideoScribe Agent Plugin

This plugin lets a local agent submit videos to VideoScribe, read transcripts and export them through stdio MCP. Jobs persist independently of the connection. An accompanying skill guides the agent through the workflow. [中文完整指南](README.md).

The [release ZIP](https://github.com/magiconline/videoscribe-agent-plugin/releases) includes the headless processing engine. It does not install another GUI app. If you clone the source, use the installer below. Both installation methods need external tools and a separate model.

Requires Apple Silicon, Python 3, and external tools:

```sh
brew install yt-dlp ffmpeg whisper.cpp node
git clone https://github.com/magiconline/videoscribe-agent-plugin.git
cd videoscribe-agent-plugin
python3 scripts/prepare-runtime.py
```

The installer reads system or terminal proxy settings and downloads with macOS curl, keeping certificate verification enabled. It checks the pinned GUI release ZIP against `runtime.json`. You can also use an installed `/Applications/VideoScribe.app`, or point `VIDEOSCRIBE_APP_PATH` to an app in another location.

Install a multilingual whisper.cpp model with the GUI repository's `scripts/download-model.sh`, or set `VIDEOSCRIBE_MODEL_PATH` to an existing model. Tools and models are installed separately. The runtime has an ad-hoc signature and has not been notarized by Apple. There is no Intel release.

Import the plugin folder in a client supporting Agent Plugins. Root `plugin.json`, `mcp.json`, and `skills/` provide the portable baseline; `.codex-plugin/` and `.mcp.json` provide a separate Codex adapter. Client support varies. Alternatively register the absolute path to `bin/videoscribe-mcp` as a stdio MCP command, with no arguments, and load `skills/video-transcript/SKILL.md` separately.

Call `get_capabilities` first. Submit with `submit_video`, poll `get_job`, and only read or export after `completed`. Export `plain`, `timed`, `srt`, or `json`. Downloads read macOS system proxy settings. Source-language transcription is supported; arbitrary translation, OCR, and diarization are not.

See [tool usage](docs/USAGE.md), [privacy](SECURITY.md), and [third-party notices](THIRD_PARTY_NOTICES.md). Tests validate manifests and installer protections; CI does not perform macOS transcription. Original code is [MIT](LICENSE).
