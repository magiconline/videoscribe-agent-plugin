# MCP 使用与任务语义

处理核心与完整接口文档维护在 [GUI 仓库](https://github.com/magiconline/videoscribe-macos/blob/main/docs/MCP.md)。本插件只是清单、skill、启动器和可校验的运行包安装入口。

| 工具 | 用途 |
| --- | --- |
| `get_capabilities` | 查看依赖、模型、系统代理与能力 |
| `submit_video` | 提交网址或绝对本地媒体路径，返回排队任务 |
| `get_job` | 查询任务，可选择读取日志 |
| `list_jobs` | 查看持久化任务 |
| `get_transcript` | 分页或按时间范围读取已完成文字稿 |
| `export_transcript` | 导出 plain / timed / srt / json |
| `cancel_job` | 请求取消指定任务 |
| `retry_job` | 创建新任务重试，保留原记录 |

任务可以是 queued、running、completed、failed、cancelled、interrupted。最多同时执行 2 个任务，最多保留 16 个未完成任务。关闭 MCP 或 GUI 不会取消 worker；重启后可能把已失去 worker 的任务标记为 interrupted，不等于自动恢复转写检查点。

文字稿每页最多 200 段，继续读取时使用返回的分页信息。分析视频时应保留原网址与时间依据。导出默认不覆盖已有文件；显式要求覆盖时才传 overwrite=true。自动语言模式不冒用不匹配语言的字幕。

## 可选环境变量

| 变量 | 作用 |
| --- | --- |
| `VIDEOSCRIBE_ENGINE_PATH` | 无界面 VideoScribeEngine 的绝对路径 |
| `VIDEOSCRIBE_APP_PATH` | VideoScribe.app 的绝对路径 |
| `VIDEOSCRIBE_MODEL_PATH` | 多语言 Whisper 模型路径 |
| `VIDEOSCRIBE_TOOL_DIR` | 优先搜索的外部工具目录 |
| `VIDEOSCRIBE_DATA_DIR` | 隔离任务目录，适合测试 |
| `PLUGIN_DATA` | 若客户端提供，启动器可从其 runtime.noindex 子目录寻找应用 |

默认数据位于当前用户 Application Support/VideoScribe。源码与安装目录可以公开，任务、日志、媒体和文字稿可能含私人内容，不能随仓库发布。系统代理按每个任务快照，失败重试应先检查网站权限和依赖，不要修改系统网络。

## 分层验证

1. `scripts/validate-plugin.py` 验证标准清单和 skill 元数据。
2. `python3 -m unittest discover -s tests -v` 验证 ZIP 路径与执行权限保护。
3. 在客户端执行 `get_capabilities`，验证实际 stdio 连接。
4. 用非私人本地媒体提交任务，等待完成并导出两个 TXT 格式，验证完整链路。

前两步成功不能替代后两步。不同客户端的本地插件安装、重启与工具发现行为应单独验证。
