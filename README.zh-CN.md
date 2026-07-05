# Hazelita Forensics Workbench

[English](README.md)

`hzltfw` 是一个面向电子数据取证课程实训的本地取证工作台。第一版目标不是做完整商业取证套件，而是跑通一个稳定的现场演示闭环：创建案件、添加准备好的 Windows 风格检材、运行分析插件、在 GUI 中查看 artifact，并导出 Markdown 报告。

## 使用

### 启动工作台

安装项目依赖并启动本地 GUI：

```bash
uv sync
uv run hzltfw
```

默认情况下，Web UI 绑定在 `127.0.0.1:8080`。如需换端口：

```bash
uv run hzltfw --host 127.0.0.1 --port 8081
```

运行时数据会写入当前工作目录下的 `.hzltfw/`：

- `.hzltfw/hzltfw.db`：本地 SQLite 数据库。
- `.hzltfw/workspace/`：检材元数据、插件输出和外部工具输出。
- `.hzltfw/config.json`：语言和外部工具命令配置。

除非课程交付明确要求导出的报告产物，否则不要提交 `.hzltfw/`、样本检材或生成报告。

### 分析检材

1. 打开本地 UI。
2. 在 **Cases** 页面创建案件。
3. 在 **Evidence** 页面添加文件、目录或压缩包检材。
4. 扫描检材，将文件索引到 `evidence_files`。
5. 在 **Analysis** 页面运行选择的内置插件。
6. 在发现中心 / artifacts 页面查看分析结果。
7. 在 **Reports** 页面导出 Markdown 报告或可携带报告包。

如果课程样本来自 Windows 镜像或 E01，请先用专门的取证工具导出目标文件，
再把导出的目录导入 `hzltfw`。详见
[docs/EVIDENCE_HANDOFF.zh-CN.md](docs/EVIDENCE_HANDOFF.zh-CN.md)。

### 配置外部工具

`hzltfw` 可以调用本机已安装的 ALEAPP、iLEAPP 和 Hindsight 适配器。外部工具
不会由本仓库安装、vendor 或提交。可以在 **Analysis** 页面的命令配置区域填写，
也可以直接编辑 `.hzltfw/config.json`。

已支持适配器：

| 工具 | 推荐输入 | 说明 |
| --- | --- | --- |
| ALEAPP | Android 文件系统导出目录或压缩包 | 输入类型使用 `fs`、`zip`、`tar` 或 `gz`。 |
| iLEAPP | iOS/iPadOS 文件系统、iTunes 备份或压缩包 | 输入类型使用 `fs`、`zip`、`tar`、`gz`、`itunes` 或 `file`。 |
| Hindsight | 浏览器 profile 目录 | 优先给完整 Chrome/Edge/Chromium profile 目录，不建议只给单个 `History`。 |

示例 `.hzltfw/config.json`：

```json
{
  "language": "zh-CN",
  "external_tools": {
    "aleapp": {
      "name": "aleapp",
      "command": ["python", "/path/to/ALEAPP/aleapp.py"],
      "enabled": true
    },
    "ileapp": {
      "name": "ileapp",
      "command": ["/path/to/ileapp"],
      "enabled": true
    },
    "hindsight": {
      "name": "hindsight",
      "command": ["python", "/path/to/hindsight.py"],
      "enabled": true
    }
  }
}
```

每个 `command` 都必须是 JSON 字符串数组。不要使用 shell alias、管道、重定向、
环境变量展开或平台专属 shell 语法；程序会用 `shell=False` 调用命令，以保持
Windows/Linux 跨平台。

推荐命令示例：

```json
["C:\\Tools\\ALEAPP\\.venv\\Scripts\\python.exe", "C:\\Tools\\ALEAPP\\aleapp.py"]
["C:\\Tools\\iLEAPP\\iLEAPP.exe"]
["C:\\Tools\\hindsight\\.venv\\Scripts\\python.exe", "C:\\Tools\\hindsight\\hindsight.py"]
```

```json
["/opt/ALEAPP/.venv/bin/python", "/opt/ALEAPP/aleapp.py"]
["/opt/iLEAPP/iLEAPP.AppImage"]
["/opt/hindsight/.venv/bin/python", "/opt/hindsight/hindsight.py"]
```

如果使用源码版工具，建议优先使用该工具自己的虚拟环境 Python，不要复用
`hzltfw` 的 Python 环境。这样 ALEAPP、iLEAPP 和 Hindsight 的依赖冲突会被隔离。

运行外部分析的流程：

1. 添加并扫描检材。
2. 打开 **Analysis** 页面。
3. 检查外部工具健康状态。健康检查会用 `--help` 调用配置好的命令。
4. 将检材探测结果作为提示，再由操作员选择工具和输入类型。
5. 启动外部工具运行，并等待执行完成。
6. 打开生成的 `external.report` artifact，或导出报告包。

外部工具每次运行会写入：

```text
.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/
```

涉及外部工具时，建议使用 **Report bundle** 导出。报告包会复制外部 HTML/JSONL/XLSX
输出，并从 `report.md` 使用相对链接引用，方便提交和在另一台机器上打开。更多细节见
[docs/EXTERNAL_TOOLS.zh-CN.md](docs/EXTERNAL_TOOLS.zh-CN.md)。

## 部署开发

### 基础要求

- Python 3.12+
- uv
- Git
- 可选：支持 flakes 的 Nix

应用技术栈为 Python、NiceGUI、SQLite、SQLModel、ruff 和 pytest。

### Linux

```bash
git clone <repo-url>
cd hzltfw
uv sync --dev
uv run hzltfw
```

如果使用 release 压缩包而不是 Git checkout，先解压并进入项目目录，然后执行同样的
`uv sync --dev` 和 `uv run hzltfw` 命令。

如果使用 Nix：

```bash
nix develop
uv sync --dev
uv run hzltfw
```

Linux 外部工具可以配置为 Python 源码目录、独立可执行文件或 AppImage。如果目标机器
因为 FUSE 缺失无法直接运行 AppImage，可以按该外部工具支持的方式解包，或改用对应的
二进制 / 源码部署方式。

### Windows

安装 Python 3.12+、Git 和 uv 后运行：

```powershell
git clone <repo-url>
cd hzltfw
uv sync --dev
uv run hzltfw
```

如果使用 release 压缩包，先解压，在项目目录打开 PowerShell，然后执行同样的
`uv sync --dev` 和 `uv run hzltfw` 命令。

在 `.hzltfw/config.json` 中使用 Windows 路径时，需要按 JSON 规则转义反斜杠：

```json
["C:\\Tools\\ALEAPP\\.venv\\Scripts\\python.exe", "C:\\Tools\\ALEAPP\\aleapp.py"]
```

源码版 ALEAPP、iLEAPP 和 Hindsight 建议各自使用独立虚拟环境。如果工具提供 Windows
可执行文件，则可以直接把命令指向该可执行文件。

### 开发检查

提交 PR 或发布前运行：

```bash
uv run ruff check .
uv run pytest
```

## 发布

当前正式版本：`v1.0.0`。

这是第一个大作业正式交付版本。该版本保留本地 NiceGUI 工作流，包含内置
artifact 插件、可选 ALEAPP/iLEAPP/Hindsight 外部工具适配、中英双语主界面，
并支持可携带报告包导出。发布范围、演示路径和已知边界见
[docs/RELEASE_NOTES.zh-CN.md](docs/RELEASE_NOTES.zh-CN.md)。

## 协作

所有功能开发都必须通过 Pull Request。不要直接 push 到 `main`。

轻量 Git 协作流程、分支命名、PR 检查清单和 AI coding 规则见 [docs/CONTRIBUTING.zh-CN.md](docs/CONTRIBUTING.zh-CN.md)。

插件开发应遵守 [docs/PLUGIN_CONTACT.zh-CN.md](docs/PLUGIN_CONTACT.zh-CN.md) 和 [docs/PLUGIN_TASKS.zh-CN.md](docs/PLUGIN_TASKS.zh-CN.md)。
如果课程样本来自 Windows 镜像或 E01，请先导出选定文件，并使用
[docs/EVIDENCE_HANDOFF.zh-CN.md](docs/EVIDENCE_HANDOFF.zh-CN.md) 检查导出目录。
ALEAPP、iLEAPP、Hindsight 和报告包导出说明见
[docs/EXTERNAL_TOOLS.zh-CN.md](docs/EXTERNAL_TOOLS.zh-CN.md)。

## 计划工具能力

课程要求按“工具能力”计数，不按插件数量计数。MVP 通过少量插件覆盖这些能力：

| 能力 | 模块 |
| --- | --- |
| 案件创建 | core/UI |
| 检材导入 | core/UI |
| 检材目录扫描 | scanner |
| 文件清单生成 | `hash_manifest` |
| MD5 计算 | `hash_manifest` |
| SHA1 计算 | `hash_manifest` |
| SHA256 计算 | `hash_manifest` |
| 文件大小和时间戳采集 | scanner |
| magic bytes 文件类型识别 | `file_type` |
| 扩展名伪装检测 | `file_type` |
| 关键词搜索 | `keyword_search` |
| 正则搜索 | `keyword_search` |
| 图片 EXIF 提取 | `metadata_extract` |
| PDF 元数据提取 | `metadata_extract` |
| DOCX 元数据提取 | `metadata_extract` |
| 压缩包索引 | `archive_index` |
| 已导出 Windows 证据摄取检查 | evidence UI/core |
| 时间线生成 | artifact/report 聚合 |
| Chromium 历史记录解析 | `browser_history` 加分项 |
| 统一 artifact 查看 | UI |
| Markdown 报告导出 | report generator |
| 外部 ALEAPP/iLEAPP/Hindsight 适配 | `external_forensics` |
| 可携带报告包导出 | report generator |

`browser_history` 是加分项。如果 Day 5 结束时仍不稳定，应保留为 planned/experimental，不得阻塞主流程。
