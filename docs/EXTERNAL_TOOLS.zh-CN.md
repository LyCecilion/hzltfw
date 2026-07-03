# 外部工具

[English](EXTERNAL_TOOLS.md)

`hzltfw` 可以调用本机已安装的外部取证工具，并把输出保存在案件工作区。
外部工具本身不会 vendor、提交或由本仓库自动安装。

## 已支持适配器

| 工具 | 用途 | 输入 |
| --- | --- | --- |
| ALEAPP | Android 导出检材分析 | `fs`, `zip`, `tar`, `gz` |
| iLEAPP | iOS/iPadOS 导出检材分析 | `fs`, `zip`, `tar`, `gz`, `itunes`, `file` |
| Hindsight | Chromium/Firefox 浏览器痕迹分析 | 浏览器 profile 目录 |

Analysis 页面可以先对证据路径做轻量探测。探测只读取目录路径或压缩包成员名，
给出可能的工具建议；最终仍由操作员选择工具和输入类型。

## 配置

外部工具命令保存在 `.hzltfw/config.json`。

示例：

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

每个命令必须是 JSON 字符串数组。不要使用 shell 专属语法、管道、别名或环境
变量展开，这样 Windows 和 Linux 都能按同一套逻辑调用。

Windows 示例：

```json
["py", "-3", "C:\\Tools\\ALEAPP\\aleapp.py"]
["C:\\Tools\\ileapp.exe"]
```

Linux 示例：

```json
["python3", "/opt/ALEAPP/aleapp.py"]
["/opt/ileapp"]
```

## 输出和报告包

每次运行写入：

```text
.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/
```

插件会生成标准 `external.report` artifact，记录输出目录、报告入口、命令、
stdout 和 stderr 摘要。

Reports 页面有两种导出：

- Markdown：只写一个 Markdown 文件。
- Report bundle：写出 `report.md`，并复制 `external/<tool>/<run-id>/...`。

大作业提交建议使用报告包，因为外部 HTML/JSONL/XLSX 输出会被一起复制，并在
Markdown 中使用相对链接。

## 跨平台说明

- `hzltfw` 不自动安装外部工具。
- Health check 会检查配置命令能否运行 `--help`。
- 命令使用 `subprocess.run(..., shell=False)` 执行。
- 路径使用 `pathlib` 处理。
- Hindsight 应输入浏览器 profile 目录，不建议只给单个 `History` SQLite 文件。
