# 贡献规范

[English](CONTRIBUTING.md)

本项目使用轻量 PR 协作流程。不要直接把功能代码 push 到 `main`。

## 分支模型

- `main` 是稳定集成分支。
- 所有改动都必须在短生命周期分支上完成，并通过 Pull Request 合并。
- 分支要聚焦。一个分支只解决一个任务或一个插件。
- 分支合并后删除。

推荐分支命名：

```text
core/scanner
core/plugin-runner
ui/artifacts-page
plugin/hash-manifest
plugin/file-type
plugin/keyword-search
docs/git-workflow
fix/windows-paths
```

前缀含义：

- `core/`：数据库、扫描器、runner、报告、共享架构。
- `ui/`：NiceGUI 页面和组件。
- `plugin/`：分析插件。
- `docs/`：文档。
- `fix/`：bug 修复。
- `test/`：只改测试。

## 日常流程

1. 从最新 `main` 开始。

   ```bash
   git switch main
   git pull
   ```

2. 创建分支。

   ```bash
   git switch -c plugin/file-type
   ```

3. 提交小而相关的改动。

   ```bash
   git status
   git add .
   git commit -m "feat: add file type plugin"
   ```

4. 推送分支。

   ```bash
   git push -u origin plugin/file-type
   ```

5. 打开 Pull Request。

6. 等 CI 和 review。

7. 只有项目组长同意后才能合并。

## PR 规则

每个 PR 必须写清：

- 改了什么。
- 怎么测试。
- GUI 可见改动要附截图。
- 插件改动要说明插件契约相关内容。
- 如果改动涉及路径、文件、SQLite 或依赖，要写 Windows 测试说明。

以下情况不要合并：

- CI 失败。
- `uv run ruff check .` 失败。
- `uv run pytest` 失败。
- PR 绕过插件契约。
- 插件直接写数据库。
- 代码只在某个人机器上能跑。

## main 分支规则

- 不允许直接 commit 到 `main`。
- 不允许 force push 到 `main`。
- 最后两天不要合并大规模、未 review 的重写。
- Day 7 功能冻结。之后只合并 bug 修复、文档修复、样本/报告修复和演示稳定性改动。

## 更新分支

短分支在开 PR 前优先 rebase：

```bash
git switch main
git pull
git switch your-branch
git rebase main
```

如果 rebase 冲突看不懂，停下来问组长。不要盲目选 ours/theirs。

如果分支已经推送并且别人也在用，优先 merge，不要改写历史：

```bash
git switch your-branch
git merge main
```

## Commit Message

使用 Conventional Commits：

```text
feat: add hash manifest plugin
fix: normalize Windows paths
docs: document plugin contract
test: cover artifact export
```

避免这种提交信息：

```text
update
fix
changes
final
```

## 冲突处理规则

- 不要通过删除别人的代码来解决冲突，除非组长确认。
- 如果冲突发生在 `pyproject.toml`、`core/models.py`、`core/plugin.py` 或 `docs/PLUGIN_CONTACT.md`，合并前必须让组长看。
- 如果两个插件需要同一个 helper，把 helper 放到 `src/hzltfw/utils/`，或者先问组长，不要复制粘贴两份。

## AI Coding 规则

AI 生成的代码也必须 PR review。

使用 AI coding 工具时：

- 把 `../AGENTS.zh-CN.md`、`ARCHITECTURE.md` 和 `PLUGIN_CONTACT.zh-CN.md` 给工具看。
- 要求工具只改当前分支任务相关内容。
- 提交前自己 review 生成的代码。
- 开 PR 前运行检查。
- 不要让 AI 重写无关文件。

## 常用命令

```bash
uv sync --dev
uv run hzltfw
uv run ruff check .
uv run pytest
git status
git diff
```
