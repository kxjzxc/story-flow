# StoryFlow (daoverse)

StoryFlow 不是小说编辑器，不是笔记软件，也不是 AI 写作产品。

它是一套极小的 Codex Skill + Markdown 项目模板，用来在本地 Markdown 仓库中构建一个
**基于 Git 的可演化叙事世界系统（daoverse）**。

核心原则：

> 人负责创造与确认；AI 负责理解、总结、结构化和维护；Git 记录世界的演化历史。

## 数据模型

四种数据：

| 类型 | 维护者 | 含义 | Canon |
| --- | --- | --- | --- |
| `idea/` | 人 | 可能性事实 | 否 |
| `draft/` | 人 | 正文事实 | 是 |
| `conversation/` | AI | 创作过程记录（滚动总结） | 否 |
| `graph/` | AI + 人审核 | 结构化世界事实 | 是 |

```text
idea          → 可能是什么
draft         → 作者写了什么
conversation  → 世界是如何被讨论出来的
graph         → 当前世界是什么
```

`idea` 不是 Graph 的中间状态，只是 Graph 的一个来源。Graph 通过 `sources` 追溯到
`draft`、`idea` 或 `conversation`。

## 项目结构

```text
my-story/
  STORYFLOW.md
  ideas/
    index.md
  draft/
    index.md          # 书目索引
    <book>/index.md   # 每本书的章节索引（支持多本正文）
  graph/
    index.md          # node id → 文件路径注册表
    nodes/
      event/
      entity/
      anchor/
  _storyflow/
    conversations/    # 滚动会话总结，默认只写不读
```

`STORYFLOW.md` 是 schema 2 的项目配置，声明 `idea_roots`、`draft_roots`、
`draft_index`、`conversation_root`、`graph_root`、`graph_index`。

## 两级 Review

Graph 的每次变更经过两级独立审核，问题完全不同，不能合并成一步：

1. **Semantic Review（人确认事实）**：AI 在对话中展示候选事实（Graph update），用户确认
   事件是否真实、时间是否正确、关系是否成立、AI 是否误读、是否与已有 Canon 冲突。
   批准前不写 `graph/`。
2. **Text Review / Git Review（人审核文件变更）**：用户在 PR diff 上检查 YAML、ID、
   relation 方向、source path、index 同步与改动范围，merge 后才算 Canon。

```text
AI → Graph Candidates → Semantic Review（人确认事实）
    → AI 修改 Graph → Git PR → Text Review（人审核文件变更）→ merge → Canon
```

## 支持的工作流

- **章节审查**：对照 graph canon、idea 与前文检查时间线、人物知识、OOC、地点、归属、
  因果等一致性问题。
- **Graph 提取**：从 `draft`、`idea`、`conversation` 提取事件、实体、关系与时间线，
  每个 Node 和 Relation 都必须带 provenance；冲突内容必须先经用户决策。
- **节点探索**：从 `[[node_id]]` 出发，经 `graph/index.md` 定位节点、沿关系展开一跳。
- **想法记录**：临时灵感写入 `ideas/`，未确认前不作为 canon 证据。
- **会话总结**：每次创作对话维护结构化滚动摘要（Topic / User Intent / Discussion /
  Decisions / New Ideas / Graph Candidates / Open Questions）；Decisions 只收用户明确
  确认的内容。

## 初始化项目

```bash
./scripts/init_project.py /path/to/my-story --title "故事名称"
```

脚本只创建缺失文件，不覆盖已有内容；默认把本 Skill 安装到项目的
`.codex/skills/story-flow/`。加 `--no-install-skill` 只生成 Markdown 结构。

## 对话记录

创建会话：

```bash
./scripts/log_conversation.py start \
  --project /path/to/my-story \
  --conversation-root _storyflow/conversations \
  --title "讨论第一章问题"
```

更新滚动总结（每次调用都会替换旧的总结，即“总结再总结”）：

```bash
./scripts/log_conversation.py summarize \
  --session /path/to/session.md \
  --content-file summary.txt
```

不提供 `append` 与 `read` 子命令：原始消息不落盘，历史也不被默认当成上下文使用。

## 非目标

StoryFlow 不做：

- Markdown 编辑器、笔记管理、云同步
- 模型托管、embedding 或语义搜索
- 自动修改正文或 Canon
- 自动把 idea 提升为 graph（idea 只是来源）

Git 分支、diff、PR 与 merge 由作者负责。

## 验证

```bash
python3 -B -m unittest discover -s tests -v
```
