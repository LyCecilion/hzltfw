# 内置插件

[English](PLUGIN_TASKS.md)

本文档记录课程交付版最终保留的内置插件行为。它已经不是待办任务清单。

## 通用规则

每个插件都遵守 `src/hzltfw/core/plugin.py` 中的契约：

- 实现 `EvidencePlugin` 或 `FilePlugin`。
- 只返回 `ArtifactCreate` 对象。
- 不直接写数据库。
- 不 import 或调用 NiceGUI。
- 使用 core scanner 生成的 `EvidenceFile` 记录，不自行递归扫描检材根目录。
- 保持 Windows 兼容的路径处理。

## 默认插件集合

`src/hzltfw/core/runner.py` 默认运行这些插件：

1. `hash_manifest`
2. `file_type`
3. `keyword_search`
4. `archive_index`
5. `metadata_extract`

`external_forensics` 不属于默认运行集合。操作员需要先在 Analysis 页面配置工具
命令，再手动选择工具和输入类型启动外部分析。

## `hash_manifest`

类型：`EvidencePlugin`

用途：

- 为已索引的物理文件生成一个 manifest artifact。
- 计算 MD5、SHA1 和 SHA256。
- 包含文件大小、相对路径、虚拟路径和时间戳。

Artifact 类型：

- `hash.manifest`

预期 artifact：

- 标题：`Evidence hash manifest`
- 严重级别：`info`
- `data.files` 为每个已哈希物理文件保存一条记录。

## `file_type`

类型：`FilePlugin`

用途：

- 使用 `puremagic` 按 magic bytes 检测文件类型。
- 仅在扩展名与检测结果不一致时产出 artifact。
- 抑制正常匹配，避免发现列表刷屏。

Artifact 类型：

- `file.type_mismatch`

预期 artifact：

- 严重级别：`medium`
- `is_key`: `true`
- `data` 记录原扩展名、检测扩展名、MIME 类型、检测名称和候选扩展名。

## `keyword_search`

类型：`EvidencePlugin`

用途：

- 使用内置演示正则搜索文本类文件。
- 默认规则覆盖中国手机号、邮箱和演示学号。
- 跳过虚拟文件、大文件和非文本扩展名。
- 包含行号、命中文本和上下文片段。

Artifact 类型：

- `keyword.regex_hit`

预期 artifact：

- 严重级别：`medium`
- `is_key`: `true`
- `source_path` 指向命中文件。
- `data` 包含 `rule`、`pattern`、`line_number`、`match` 和 `snippet`。

## `archive_index`

类型：`EvidencePlugin`

用途：

- 索引 ZIP 压缩包条目，但不解压。
- 每个可读 ZIP 文件产出一个压缩包摘要 artifact。
- 对命中内置关键词或 keyword-search 正则的可疑条目名产出关键 artifact。

Artifact 类型：

- `archive.index`
- `archive.entry`

预期 artifact：

- `archive.index` 记录条目数、文件数、目录数、可疑条目数和条目元数据。
- `archive.entry` 使用 `medium` 严重级别、`is_key=true`，并记录压缩包路径、
  条目信息和命中原因。

## `metadata_extract`

类型：`FilePlugin`

用途：

- 使用 Pillow 提取图片元数据。
- 使用 `pypdf` 提取 PDF 文档元数据和页数。
- 使用 `python-docx` 提取 DOCX core properties。

Artifact 类型：

- `metadata.image`
- `metadata.pdf`
- `metadata.office`

预期 artifact：

- 图片 artifact 包含格式、模式、尺寸和可用 EXIF。
- PDF artifact 包含 metadata、页数和可解析的创建/修改时间。
- DOCX artifact 包含标题、作者、创建时间、修改时间和 comments 等 core
  properties。

## `external_forensics`

类型：`EvidencePlugin`，手动启动

用途：

- 运行本机配置好的 ALEAPP、iLEAPP 或 Hindsight 命令。
- 将外部工具输出保存在案件工作区。
- 产出报告链接和 highlight artifact，不全量导入外部工具所有结果。

Artifact 类型：

- `external.report`
- `external.highlight`

预期行为：

- 外部命令缺失时通过 health check 或失败的 plugin run 报告，不影响默认插件
  流程。
- 命令是 JSON 字符串数组，并使用 `shell=False` 运行。
- 输出写入
  `.hzltfw/workspace/case-<case-id>/external_runs/<tool>/run-<plugin-run-id>/`。
- 报告包会复制外部输出目录，并在 `report.md` 中链接。
