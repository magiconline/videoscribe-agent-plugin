# VideoScribe Agent Plugin

这个插件让本地 Agent 直接调用 VideoScribe：提交视频网址或本地媒体，提取字幕或离线转写，再读取、导出文字稿。独立 worker 负责处理任务，MCP 连接断开后也会继续运行。

[English](README.en.md) · [GUI 与处理核心](https://github.com/magiconline/videoscribe-macos) · [工具与使用指南](docs/USAGE.md)

## 安装

可以从 [Releases](https://github.com/magiconline/videoscribe-agent-plugin/releases) 下载插件 ZIP，解压后导入插件目录。ZIP 已包含无界面处理核心，可以跳过运行包准备脚本；外部工具和模型仍需单独安装。

需要一台 Apple Silicon Mac、Python 3，以及支持 stdio MCP 的本地 Agent。源码目标为 macOS 14，尚未逐一验证其他系统版本，也没有提供 Intel 发行包。下面是从源码安装的步骤：

```sh
brew install yt-dlp ffmpeg whisper.cpp node
git clone https://github.com/magiconline/videoscribe-agent-plugin.git
cd videoscribe-agent-plugin
python3 scripts/prepare-runtime.py
```

准备脚本会从 GUI 仓库下载 `runtime.json` 指定的发行包，核对固定 SHA-256，再将 Agent 程序和资源放入 `runtime.noindex/VideoScribeEngine`。这一步只安装处理核心，不会多装一个 GUI 应用。

如果已经安装 GUI，可以跳过下载，直接使用 `/Applications/VideoScribe.app`；应用放在其他位置时，将 `VIDEOSCRIBE_APP_PATH` 设为它的绝对路径。已有 ZIP 文件也可以通过 `--archive /absolute/path/VideoScribe-macOS-arm64.zip` 离线安装。源码仓库本身不包含运行程序、模型或第三方工具。

转写还需要 whisper.cpp 多语言模型。已有模型可以在 GUI 设置中选择；无界面使用时，设置 `VIDEOSCRIBE_MODEL_PATH`。也可以在 GUI 仓库运行 `scripts/download-model.sh`，将带固定校验值的 base 模型下载到默认目录。运行包使用临时签名，尚未通过 Apple 公证。

## 连接 Agent

通用 Agent Plugins：本仓库提供根目录 `plugin.json`、`mcp.json` 和 `skills/`。支持该规范的客户端可导入本地插件目录。客户端必须支持 `${PLUGIN_ROOT}` 替换和相对命令解析。

Codex 格式适配：另附 `.codex-plugin/plugin.json`、`.mcp.json` 和本地 marketplace 清单。早期本机版本已在 Codex 中完成导入和实际调用。各客户端的插件入口、路径变量支持有所不同，使用公开版本时仍需在安装后检查能力。插件名为 `videoscribe`，skill 为 `video-transcript`。

直接注册 MCP：若客户端不支持插件，请添加一个 stdio 服务，将下面路径替换为克隆目录的真实绝对路径：

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

然后通过客户端的 skill 管理器加载 `skills/video-transcript/SKILL.md`。连接后，先执行 `get_capabilities`，检查工具、模型和可执行文件是否就绪。清单解析成功只能证明格式正确，还需要实际调用来确认 MCP 可用。

## 使用

可以直接对 Agent 说：“用 VideoScribe 处理这个视频，导出带时间戳和不带时间戳的文字稿。”

Agent 应先调用 `submit_video`，再轮询 `get_job`。只有任务状态变为 `completed` 后，才调用 `get_transcript` 或 `export_transcript`。返回 `queued` 时，任务还在排队。

可以选择中文、英文，或自动识别原声语言。处理时优先读取匹配字幕，也可以强制本地转写。导出格式包括纯文字 TXT、带起止时间戳的 TXT、SRT 和 JSON。插件不提供任意语言互译、OCR 或说话人区分。

每个网络任务主动读取 macOS 系统代理及源网址例外规则，不更改系统设置。引导下载脚本使用 Python 读取系统/终端代理，并交给 macOS 自带 curl 下载（保留系统证书验证）；如网络环境要求，可在终端设置 `https_proxy`。PAC 和认证代理尚未完成真实环境验证。

## 开发与安全

```sh
python3 -m pip install jsonschema PyYAML
python3 scripts/validate-plugin.py
python3 -m unittest discover -s tests -v
python3 scripts/privacy-scan.py
```

CI 会检查清单、skill 元数据、运行包安装保护和源文件，其中不包含 macOS 视频转写测试。请勿提交运行数据、模型、媒体、日志或账号文件。MCP 使用当前用户的权限，只应连接可信 Agent。详见 [安全说明](SECURITY.md) 与 [第三方说明](THIRD_PARTY_NOTICES.md)。

原创代码采用 [MIT](LICENSE)。
