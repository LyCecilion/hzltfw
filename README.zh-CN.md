# Hazelita Forensics Workbench

[English](README.md)

`hzltfw` 是一个面向电子数据取证课程实训的本地取证工作台。第一版目标不是做完整商业取证套件，而是跑通一个稳定的现场演示闭环：创建案件、添加准备好的 Windows 风格检材、运行分析插件、在 GUI 中查看 artifact，并导出 Markdown 报告。

## MVP 流程

1. 创建案件。
2. 添加文件或目录检材。
3. 将检材扫描为 `evidence_files`。
4. 运行选择的分析插件。
5. 存储统一格式的 artifacts。
6. 在 GUI 中查看分析结果和可进入时间线的结果。
7. 导出 Markdown 取证报告。

## 技术栈

- Python 3.12+
- uv
- NiceGUI
- SQLite
- SQLModel
- ruff
- pytest
- 可选：通过 `flake.nix` 使用 Nix 开发环境

## 开发

```bash
uv sync --dev
uv run hzltfw
```

运行检查：

```bash
uv run ruff check .
uv run pytest
```

使用 Determinate Nix 或其他支持 flakes 的 Nix：

```bash
nix develop
uv sync --dev
```

## 协作

所有功能开发都必须通过 Pull Request。不要直接 push 到 `main`。

轻量 Git 协作流程、分支命名、PR 检查清单和 AI coding 规则见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)。

插件开发应遵守 [PLUGIN_CONTACT.zh-CN.md](PLUGIN_CONTACT.zh-CN.md) 和 [PLUGIN_TASKS.zh-CN.md](PLUGIN_TASKS.zh-CN.md)。
如果课程样本来自 Windows 镜像或 E01，请先导出选定文件，并使用
[EVIDENCE_HANDOFF.zh-CN.md](EVIDENCE_HANDOFF.zh-CN.md) 检查导出目录。

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
| 压缩包索引 | `archive_index` |
| 时间线生成 | artifact/report 聚合 |
| Chromium 历史记录解析 | `browser_history` 加分项 |
| 统一 artifact 查看 | UI |
| Markdown 报告导出 | report generator |

`browser_history` 是加分项。如果 Day 5 结束时仍不稳定，应保留为 planned/experimental，不得阻塞主流程。
