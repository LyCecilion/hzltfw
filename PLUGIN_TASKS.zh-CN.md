# 插件任务

[English](PLUGIN_TASKS.md)

本文档定义 MVP 阶段各插件的预期工作。可以直接拿来开 GitHub issue 和 PR checklist。

## 通用完成规则

每个插件必须：

- 实现 `src/hzltfw/core/plugin.py` 中的 `EvidencePlugin` 或 `FilePlugin`。
- 只返回 `ArtifactCreate` 对象。
- 不直接写数据库。
- 不 import GUI。
- 使用 `EvidenceFile.relative_path`、`absolute_path` 和 `virtual_path`，不要重新扫描检材根目录。
- 至少添加一个测试，或用最小样本更新 `tests/test_smoke.py`。
- 在 PR 中说明会产出的 artifact 类型。
- 能在 Windows 上运行。

## `hash_manifest`

状态：已实现，是第一个 `EvidencePlugin` 示例。

用途：

- 为所有已索引的物理文件生成 manifest。
- 计算 MD5、SHA1 和 SHA256。
- 包含文件大小和时间戳。

Artifact 类型：

- `hash.manifest`

MVP 完成标准：

- 一个目录检材能产出一个 manifest artifact。
- 开启 `include_manifest` 时，报告可以包含完整 manifest。

## `file_type`

状态：已实现，是第一个 `FilePlugin` 示例。

用途：

- 根据 magic bytes 检测文件类型。
- 记录检测出的扩展名、MIME、显示名称和置信度。
- 将扩展名不一致标记为关键 warning artifact。

Artifact 类型：

- `file.type`
- `file.type_mismatch`

MVP 完成标准：

- 普通文件产出 `file.type` artifact。
- 类似 `fake.jpg` 但内容是 PDF 或 ZIP bytes 的文件产出 `file.type_mismatch`。
- mismatch artifact 使用 `severity="medium"` 且 `is_key=True`。

## `keyword_search`

建议负责人任务。

插件类型：`EvidencePlugin`。

用途：

- 对文本类文件搜索配置的关键词。
- 支持简单正则。
- 每个命中包含一小段上下文。
- 默认跳过大型二进制文件。

建议配置：

```json
{
  "keywords": ["泄露", "密码", "课程资料"],
  "regexes": ["[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"]
}
```

Artifact 类型：

- `keyword.hit`
- `keyword.regex_hit`

MVP 完成标准：

- 含关键词的 `.txt` 样本能产出 hit artifact。
- 含邮箱地址的样本能产出 regex hit artifact。
- artifact 的 `data` 包含 `source_path`、`line_number`、`match` 和 `snippet`。

## `archive_index`

建议负责人任务。

插件类型：`EvidencePlugin`。

用途：

- 优先索引 ZIP 文件。
- 有时间再支持 TAR。
- ZIP/TAR 稳定后再通过 `py7zr` 加 7z。
- MVP 不自动解压压缩包内容。

Artifact 类型：

- `archive.index`
- `archive.entry`

MVP 完成标准：

- ZIP 样本能产出压缩包摘要 artifact。
- 压缩包条目包含路径、解压后大小、压缩后大小和修改时间。
- 可疑条目名可以打 `keyword` 或 `suspicious_name` 等 tag。

## `metadata_extract`

建议负责人任务。

插件类型：`FilePlugin`。

用途：

- 通过 Pillow 提取图片元数据。
- 通过 `pypdf` 提取 PDF 文档元数据。
- 有时间再提取 Office 基础元数据。

Artifact 类型：

- `metadata.image`
- `metadata.pdf`
- `metadata.office`

MVP 完成标准：

- 带 EXIF 的 JPEG 能产出相机/时间元数据。
- PDF 样本能产出 title、author、creator、producer、页数等信息。
- 元数据时间可靠时，artifact 使用 timestamp 字段。

## `browser_history`

加分项。不得阻塞主流程。

插件类型：`FilePlugin`。

用途：

- 识别 Chromium `History` SQLite 数据库。
- 解析 URL 访问记录。
- 有时间再解析下载记录。
- 规范化 Chromium 时间戳。

Artifact 类型：

- `browser.history`
- `browser.download`

MVP 完成标准：

- 准备好的 Chromium `History` 样本能产出访问记录 artifact。
- 每条访问记录包含 URL、标题、访问时间、访问次数和源数据库路径。
- artifact 能进入报告时间线。

砍功能规则：

- 如果 Day 5 结束还不稳定，就保留为 planned/experimental，并从现场演示主线移除。
