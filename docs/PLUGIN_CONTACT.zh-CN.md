# 插件契约

[English](PLUGIN_CONTACT.md)

这是插件作者必须遵守的接口文档。

## 硬规则

- 插件不得直接写数据库。
- 插件不得 import 或调用 NiceGUI。
- 插件不得自己递归扫描检材根目录。必须使用 core scanner 提供的 `EvidenceFile` 记录。
- 插件不得发明自己的路径格式。使用 `relative_path`、`absolute_path` 和 `virtual_path`。
- 插件只返回 `ArtifactCreate` 对象。
- 插件无法继续时可以抛异常。runner 会记录该插件失败，并继续运行其他插件。
- 必须保持 Windows 兼容。避免 Linux-only 依赖和路径假设。

## 插件类型

### EvidencePlugin

当插件需要分析整个检材或一组文件时使用。

例子：

- `hash_manifest`
- `archive_index`
- `keyword_search`

### FilePlugin

当插件一次只分析一个文件时使用。

例子：

- `file_type`
- `metadata_extract`
- `browser_history`

### 外部工具适配器

`external_forensics` 这类适配器以 `EvidencePlugin` 实现。它们可以调用本机
已配置的命令，但仍然只能返回 `ArtifactCreate`，不得直接写数据库，也不得调用
GUI。

外部工具在 `.hzltfw/config.json` 中配置。不要把外部工具源码树或二进制文件
vendor 到本仓库。

## ArtifactCreate 字段

```text
artifact_type: str
title: str
summary: str
source_path: str | None
timestamp: datetime | None
severity: "info" | "low" | "medium" | "high"
is_key: bool
tags: list[str]
data: dict
```

通用字段用于展示、搜索和报告。插件特有详情放进 `data`。

## severity 使用建议

- `info`：普通证据事实，例如 manifest 生成。
- `low`：值得注意但预期内的记录。
- `medium`：可疑发现，例如关键词命中、扩展名伪装。
- `high`：演示故事线中的强关键发现。

## 插件 PR 必须包含

- 插件名称和用途。
- 支持的输入。
- 依赖。
- 会产出的 artifact 类型。
- 最小样本或样本说明。
- 预期 artifact 示例。
- Windows 测试说明。
- 外部工具适配器还必须说明安装/配置方式，以及预期输出文件或报告入口路径。

## Artifact 示例

```python
ArtifactCreate(
    artifact_type="file.type_mismatch",
    title="扩展名与检测类型不一致",
    summary="Downloads/photo.jpg 看起来是 ZIP archive",
    source_path="Downloads/photo.jpg",
    timestamp=file.mtime,
    severity="medium",
    is_key=True,
    tags=["mismatch", "suspicious"],
    data={
        "extension": ".jpg",
        "detected_type": "application/zip",
    },
)
```
