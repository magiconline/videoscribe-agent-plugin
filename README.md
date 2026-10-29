# VideoScribe Agent Plugin

让本地 Agent 通过 MCP 提交视频网址或本地媒体，提取字幕、离线转写并读取或导出文字稿。任务由独立 worker 执行，MCP 断开后仍继续。

[English](README.en.md) · [GUI 与处理核心](https://github.com/magiconline/videoscribe-macos) · [工具与使用指南](docs/USAGE.md)

## 安装

也可从 [Releases](https://github.com/magiconline/videoscribe-agent-plugin/releases) 下载含精简运行程序的插件 ZIP，解压后直接导入插件目录；仍需安装下面的外部工具和模型，无需再运行运行包准备脚本。

需要 Apple Silicon Mac、Python 3 和本地 Agent 的 stdio MCP 支持。源码目标 macOS 14，未逐一验证所有系统版本；不提供 Intel 发行包。

```sh
brew install yt-dlp ffmpeg whisper.cpp node
git clone https://github.com/magiconline/videoscribe-agent-plugin.git
cd videoscribe-agent-plugin
python3 scripts/prepare-runtime.py
```

准备脚本下载 `runtime.json` 指定的 GUI 仓库发行包，校验固定 SHA-256，再解压到 `runtime/VideoScribe.app`。若已安装 GUI，可跳过下载，直接使用 `/Applications/VideoScribe.app`，或设置 `VIDEOSCRIBE_APP_PATH` 为应用的绝对路径。已有 ZIP 可用 `--archive /absolute/path/VideoScribe-macOS-arm64.zip` 离线安装。源码仓库不提交运行程序、模型或第三方工具。

还需要 whisper.cpp 多语言模型。可在 GUI 设置中选择已有模型；无界面使用时设置 `VIDEOSCRIBE_MODEL_PATH`，或从 GUI 仓库运行 `scripts/download-model.sh` 下载带固定校验值的 base 模型到默认目录。运行包是临时签名，未做 Apple 公证。

## 连接 Agent

**通用 Agent Plugins**：本仓库提供根目录 `plugin.json`、`mcp.json` 和 `skills/`。支持该规范的客户端可导入本地插件目录。客户端必须支持 `${PLUGIN_ROOT}` 替换和相对命令解析。

**Codex 格式适配**：另附 `.codex-plugin/plugin.json`、`.mcp.json` 和本地 marketplace 清单。已验证的早期本机版本可被 Codex 导入及实际调用；不同客户端的插件入口与路径变量支持不同，本次公开版本以安装后能力检查为准。插件名为 `videoscribe`，skill 为 `video-transcript`。

**直接注册 MCP**：若客户端不支持插件，请添加一个 stdio 服务，将下面路径替换为克隆目录的真实绝对路径：

```json
{
  "mcpServers": {
    "videoscribe": {
      "command": "/absolute/path/videoscribe-agent-plugin/bin/videoscribe-mcp",
      "args": []
    }
  }
}
```

并将 `skills/video-transcript/SKILL.md` 交给客户端的 skill 管理器。客户端能解析清单不等于已能调用 MCP；连接后先执行 `get_capabilities`，确认工具、模型和可执行文件都已就绪。

## 使用

向 Agent 说明：“用 VideoScribe 处理这个视频，导出带时间戳和不带时间戳的文字稿。”Agent 应先 `submit_video`，轮询 `get_job`，仅在 `completed` 后读取 `get_transcript` 或 `export_transcript`。提交返回 `queued` 不表示完成。

支持中文、英文和自动识别原声语言；优先使用匹配字幕，或强制本地转写。提供纯文字 TXT、带起止时间戳 TXT、SRT、JSON。它不会自动把任意内容翻译成另一种语言，也不做 OCR 或说话人区分。

每个网络任务主动读取 macOS 系统代理及源网址例外规则，不更改系统设置。引导下载脚本使用 Python 的代理发现；如网络环境要求，可在终端设置 `https_proxy`。PAC 和认证代理尚未完成真实环境验证。

## 开发与安全

```sh
python3 -m pip install jsonschema PyYAML
python3 scripts/validate-plugin.py
python3 -m unittest discover -s tests -v
python3 scripts/privacy-scan.py
```

CI 只验证清单、skill 元数据、运行包安装保护与源文件扫描；不代表 CI 已执行 macOS 视频转写。运行数据、模型、媒体、日志和账号文件均不应提交。MCP 使用当前用户权限，请只连接可信 Agent。详见 [安全说明](SECURITY.md) 与 [第三方说明](THIRD_PARTY_NOTICES.md)。

原创代码采用 [MIT](LICENSE)。
