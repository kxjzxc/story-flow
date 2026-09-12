# StoryFlow (daoverse)

StoryFlow 不是小说编辑器，不是笔记软件，也不是 AI 写作产品。

它是一套极小的 Codex Skill + Markdown 项目模板，用来在本地 Markdown 仓库中构建一个
**基于 Git 的可演化叙事世界系统（daoverse）**。

核心原则：

> 人负责创造与确认；AI 负责理解、总结、结构化和维护；Git 记录世界的演化历史。

## 数据模型

三种数据类型：

| 类型 | 维护者 | 含义 | Canon |
| --- | --- | --- | --- |
| `idea` | 人 + AI | 创作过程中产生、讨论和整理的非 Canon 内容 | 否 |
| `draft` | 人 | 正文事实 | 是 |
| `graph` | AI + 人 | 结构化世界事实 | 是 |

```text
idea  → 创作过程中正在形成什么
 draft → 作者已经写了什么
 graph → 当前世界是什么
```

`idea` 是人和 AI 共同使用的创作工作区，而不是只有“临时灵感”的存储区。用户可以直接
编辑 Idea；AI 也可以在对话中整理和总结讨论结论，并写回对应 Idea。Idea 中的内容始终
不是 Canon，但可以作为 Graph 或 Draft 变更的来源。

AI 不需要把每次对话保存成独立的 `conversation` 文件。对话本身是即时创作过程；值得
保留的内容由 AI 总结进 `ideas/`。

## 项目结构

```text
my-story/
  STORYFLOW.md
  ideas/
    index.md
    ...
  draft/
    index.md          # 书目索引
    <book>/index.md   # 每本书的章节索引（支持多本正文）
  graph/
    index.md          # node id → 文件路径注册表
    nodes/
      event/
      entity/
      anchor/
```

`STORYFLOW.md` 是 schema 2 的项目配置，声明 `idea_roots`、`draft_roots`、`draft_index`、
`graph_root`、`graph_index`。

## 创作与变更流程

一次创作对话中，用户可以要求 AI 整理当前讨论并提 PR。AI 负责：

1. 将值得保留的讨论结论、设定想法和未决方向整理进 `ideas/`；
2. 从这些内容以及现有 Canon 中识别应该更新的 Graph 内容；
3. 直接修改对应的 `ideas/` 和 `graph/` 文件；
4. 创建 Git commit 和 PR。

用户负责 PR 的最终审查与 merge。AI 不执行 merge。

```text
创作对话
   ↓
Ideas（人 + AI 共同编辑）
   ↓
AI 整理 Ideas / 更新 Graph
   ↓
Git PR
   ↓
用户 Review
   ├── 提出意见 → AI 修改 PR
   └── Merge → Main / Canon
```

## AI Review

用户也可以要求 AI Review 一个 PR。此时 AI 的职责不是替用户决定是否合入，而是基于
`main` 当前的 Graph 和 Draft 判断 PR 新增内容是否合理。

重点检查：

- 是否与现有 Graph Canon 冲突；
- 是否与正文已经发生的事实冲突；
- 时间线是否成立；
- Entity 的行为、关系和状态是否符合已有内容；
- 新增事件是否具有合理的因果关系；
- 是否存在明显的逻辑漏洞。

AI Review 的结果只是审查意见。最终是否修改、接受或 merge，由用户决定。

## Graph 模型

Graph 是当前世界的结构化 Canon：

- `event` — 世界中发生的事情；
- `entity` — 持续存在的角色、组织、地点、物品或其他对象；
- `anchor` — 对世界演化具有强约束的事件或状态；
- `relation` — 节点之间的结构化关系。

每个 Node 和 Relation 都必须带 provenance，指向产生该内容的 `draft` 或 `idea`。Git
记录 Canon 如何随 PR 演化。

## 支持的工作流

- **章节审查**：对照 graph canon、idea 与前文检查时间线、人物知识、OOC、地点、归属、
  因果等一致性。
- **Graph 提取**：从 `draft` 和 `idea` 提取事件、实体、关系与时间线，每个 Node 和
  Relation 都必须带 provenance；冲突内容通过 PR 暴露给用户处理。
- **节点探索**：从 `[[node_id]]` 出发，经 `graph/index.md` 定位节点、沿关系展开一跳。
- **想法整理**：人可以直接编辑 `ideas/`；AI 可以根据创作对话总结、合并和整理 Idea。
- **PR Review**：AI 根据 main 的 Graph 和 Draft 检查新增内容是否符合现有世界逻辑；用户
  负责最终审查和 merge。

## 初始化项目

```bash
./scripts/init_project.py /path/to/my-story --title "故事名称"
```

脚本只创建缺失文件，不覆盖已有内容；默认把本 Skill 安装到项目的
`.codex/skills/story-flow/`。加 `--no-install-skill` 只生成 Markdown 结构。

## 非目标

StoryFlow 不做：

- Markdown 编辑器、笔记管理、云同步
- 模型托管、embedding 或语义搜索
- 自动修改正文
- 自动把 idea 变成 Canon 而不经过 Git PR
- 代表用户 merge PR

Git 分支、diff、PR 与 merge 仍由 GitHub 和作者承担最终控制。

## 验证

```bash
python3 -B -m unittest discover -s tests -v
```
