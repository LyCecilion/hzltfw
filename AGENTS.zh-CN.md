# AGENTS.md

[English](AGENTS.md)

本仓库是 Hazelita Forensics Workbench (`hzltfw`)，一个面向课程实训的本地电子数据取证工作台。AI coding agent 必须保持项目在短工期内可控，避免架构漂移。

- 以瞎猜接口为耻，以认真查询为荣。
- 以模糊执行为耻，以寻求确认为荣。
- 以臆想业务为耻，以人类确认为荣。
- 以创造接口为耻，以复用现有为荣。
- 以跳过验证为耻，以主动测试为荣。
- 以破坏架构为耻，以遵循规范为荣。
- 以假装理解为耻，以诚实无知为荣。
- 以盲目修改为耻，以谨慎重构为荣。

## 产品范围

- 主要场景：电子数据取证课程实训和现场演示。
- MVP 流程：创建案件、添加检材、扫描文件、运行插件、查看 artifacts、导出 Markdown 报告。
- 必须有 GUI：NiceGUI 本地 Web UI。
- 必须使用包管理流程：`uv`。
- Windows 兼容性是合并条件。Fedora/Linux 支持不能依赖 Linux-only 行为。

## 架构规则

- 保持分层结构：
  - `core/`：数据库、模型、workspace、scanner、插件契约、runner、报告生成。
  - `plugins/`：解析器和分析器实现。
  - `ui/`：NiceGUI 页面和组件。
  - `utils/`：小型共享 helper。
- Evidence 是用户导入的检材：一个目录或一个文件。
- `evidence_files` 是检材内部发现并索引出来的资源。
- core scanner 负责目录遍历和路径规范化。
- 插件不得自己递归扫描检材根目录。
- 插件不得直接写数据库。
- 插件不得 import 或调用 NiceGUI。
- 插件返回 `ArtifactCreate` 对象；runner 负责持久化 artifacts 和 plugin run 状态。
- 一个插件失败只标记该插件 run 失败。其他选中的插件应继续运行。

## 数据模型规则

- 使用 SQLModel 持久化。
- 插件特有数据放在 `artifacts.data_json`。
- artifact 的公共可检索字段保留为一等列：
  - `artifact_type`
  - `title`
  - `summary`
  - `source_path`
  - `timestamp`
  - `severity`
  - `is_key`
  - `tags_json`
- 除非小组明确同意 JSON artifact 无法支撑需求，否则不要添加插件专属表。

## 插件规则

插件实现两种契约之一：

- `EvidencePlugin`：分析一个 evidence item 及其已索引文件。
- `FilePlugin`：声明 `supports(file)`，并分析匹配的文件。

每个插件贡献必须包含：

- 支持的输入和依赖。
- 会产出的 artifact 类型。
- 最小样本或样本说明。
- 预期 artifact 示例。
- Windows 测试说明。

插件契约以 `PLUGIN_CONTACT.zh-CN.md` 为准。

## 代码风格

- 公共函数和 dataclass 使用类型标注。
- 优先写输入明确的小函数，避免隐藏全局状态。
- 注释少而有用。
- 文件系统路径使用 `pathlib.Path`。
- 数据库时间戳使用带时区的 UTC datetime。
- 避免平台特定路径解析。使用 `Path` 和已存储的 relative/virtual path。
- 未经同意，不引入大型框架或后台任务系统。

## 命令

- 安装依赖：`uv sync --dev`
- 启动 GUI：`uv run hzltfw`
- 运行测试：`uv run pytest`
- Lint：`uv run ruff check .`

## 工期纪律

- Day 7 功能冻结。
- Chromium History 是加分项。如果 Day 5 仍未完成，保留接口占位，主流程继续工作。
- 不要为了压缩包递归、专属 artifact 页面或高级报告样式阻塞主流程。

## Git 工作流

- 遵守 `CONTRIBUTING.zh-CN.md`。
- 不要直接 commit 到 `main`。
- 所有改动必须通过 Pull Request。
- 分支要短生命周期，并聚焦一个任务。
- 未经 review，不要通过改写他人工作来解决冲突。
- AI 生成的代码同样需要人工 review 和 CI。
