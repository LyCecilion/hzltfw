# Windows 证据交接指南

[English](EVIDENCE_HANDOFF.md)

`hzltfw` 分析的是已经导出的文件和目录。MVP 工作流不直接解析 E01
镜像、分区表或 NTFS 文件系统。

推荐流程：

1. 使用 FTK Imager、Autopsy、X-Ways、Arsenal Image Mounter、ewf-tools 或
   The Sleuth Kit 等取证工具查看源镜像。
2. 将需要分析的 Windows 文件和目录导出成普通目录。
3. 将这个导出目录导入 `hzltfw`。
4. 运行默认插件并导出 Markdown 报告。

## 建议导出目标

| 目标 | 示例路径 | 用途 |
| --- | --- | --- |
| 用户文档和桌面 | `Users\<user>\Documents`, `Users\<user>\Desktop`, `Users\<user>\Downloads` | 文档、压缩包、下载文件和普通用户文件 |
| Chromium 配置 | `Users\<user>\AppData\Local\Google\Chrome\User Data\Default\History`, `Users\<user>\AppData\Local\Microsoft\Edge\User Data\Default\History` | 可选浏览器历史解析 |
| 最近使用快捷方式 | `Users\<user>\AppData\Roaming\Microsoft\Windows\Recent` | 后续 LNK 解析 |
| 注册表 hive | `Users\<user>\NTUSER.DAT`, `Windows\System32\config\SOFTWARE`, `Windows\System32\config\SYSTEM` | 后续注册表速览 |
| Windows 事件日志 | `Windows\System32\winevt\Logs\*.evtx` | 后续 EVTX 摘要 |
| 回收站 | `$Recycle.Bin` | 后续删除文件审查 |
| 邮件和 Office 文件 | 用户目录下的 `*.msg`, `*.docx`, `*.xlsx`, `*.pptx` | 后续邮件和 Office 可疑内容插件 |

## 课程样本规则

- 尽量保留原始文件名和目录结构。
- 不要将完整证据样本提交到本仓库。
- 在文档中记录样本哈希、预期发现和交接说明。
- 课程演示样本应使用虚构个人数据。

本地 GUI 也提供 **Evidence Handoff** 页面，可针对具体案件或样本导出
Markdown 交接清单。
