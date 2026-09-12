---
name: story-flow
description: 初始化 StoryFlow 项目，检索 Ideas、正文和世界图谱，审查章节一致性，提取并维护图谱内容，根据当前主线审查 PR 的世界一致性。用于故事项目初始化、故事讨论、章节一致性与 OOC 检查、时间线分析、图谱提取、Idea 整理以及 PR 审查。
---

# StoryFlow

使用 Markdown 文件作为故事的唯一来源。回答问题前先检索证据。Ideas 是共享的创作工作区：用户和 AI 都可以编辑，但 Ideas 不是 Canon。Draft 和 Graph 属于 Canon，只有经过用户自己的 Git 工作流进入 `main` 后才成为主线 Canon。

## 数据模型

StoryFlow 有三种数据类型：

- `idea` — 由用户和 AI 共同维护的创作素材；不是 Canon。
- `draft` — 作者维护的正文 Canon。
- `graph` — 结构化的世界 Canon，包括事件、实体、锚点和关系。

这些是数据类型名称，不是目录名称。Idea 存放在 `ideas/`，`draft` 和 `graph` 分别存放在 `draft/` 和 `graph/`。

```text
idea  → 创作过程中正在形成什么
draft → 作者已经写了什么
graph → 当前世界是什么
```

Idea 可以是灵感、讨论结论、可能的设定、未决问题、被否定的方案或其他有长期价值的创作素材。用户可以直接编辑 Idea；AI 也可以在对话中整理和总结讨论结论，并写回对应的 Idea。AI 不应保存原始对话，而应优先把值得保留的内容总结成可继续使用的 Idea。

## 定位项目

1. 在当前工作文件及其父目录中寻找最近的 `STORYFLOW.md`。
2. 将该文件所在目录视为项目边界。不要跟随链接访问项目外部内容。
3. 读取 `storyflow` frontmatter 中的 `idea_roots`、`draft_roots`、`draft_index`、`graph_root` 和 `graph_index`。
4. 如果某个字段缺失，则分别使用 `ideas`、`draft`、`draft/index.md`、`graph` 和 `graph/index.md`。
5. 不创建或假设独立的 conversation archive。当前聊天就是创作过程；需要长期保留的结论，应在合适的时候整理进 `ideas/`。

每本书位于 draft root 下的一个目录中，并拥有自己的 `index.md` 来列出章节；draft root 的 `index.md` 列出各本书。如果 draft root 直接列出章节而不是书目录，则视为单本书项目。

如果不存在 manifest，应向用户询问项目根目录，或提供初始化方式：

```bash
python scripts/init_project.py PROJECT_PATH --title "故事名称"
```

初始化脚本会创建 Markdown 项目文件，并默认将本 Skill 安装到 `PROJECT_PATH/.codex/skills/story-flow/`。只有用户明确要求纯 Markdown 模板时，才使用 `--no-install-skill`。

## 访问边界

- 只在当前任务需要时读取 Idea、Draft 和 Graph 文件。
- Idea 是非 Canon 的工作素材。不得把 Idea 当成已经确定的世界事实。
- 用户和 AI 都可以编辑 Idea。当用户要求保存、记录或总结讨论结论时，应将其整理进相关 Idea，而不是创建 conversation 记录。
- Graph 是 Canon。用户明确要求准备 PR 时，AI 可以在 PR 分支上更新 Graph；这些修改在用户合入 `main` 前都不属于主线 Canon。
- 不得凭空创造 Graph 事实。每个节点和关系都必须通过 provenance 指向 `draft` 或 `idea` 来源。
- 默认不要编辑 Draft 及其索引。分析 Draft 时应在回复中提供报告或建议文本。
- AI 绝不能代替用户合并 PR。

## 检索故事上下文

1. 从用户请求中提取姓名、别名、节点 ID、地点、组织、事件、物品、规则和独特短语。
2. 如果请求中明确给出节点 ID，先通过 `graph_index` 定位，再读取节点文件；沿 `relations` 展开一跳，必要时读取其来源。
3. 在配置的 Idea 和 Draft 根目录中检索。优先使用准确标题、frontmatter alias 和精确短语，再进行宽泛关键词搜索。
4. 解析 `[[note]]`、`[[note|label]]` 和相对路径 Markdown 链接。
5. 对强匹配结果展开直接链接和反向链接一跳。按 frontmatter `storyflow.id`、相对路径、文件名、alias 的顺序解析。链接存在歧义时不要猜测，应明确报告。
6. 证据优先级：明确指定的文件 > 索引条目 > 精确匹配 > 链接到的笔记 > 宽泛关键词匹配。
7. 对事实性回答给出相关路径和标题，并区分项目证据与推断。

不要使用 embedding 或建立持久化索引。使用文件列表、文本搜索、链接和定向读取即可。

## Graph 模型

- 节点位于 `graph/nodes/{event,entity,anchor}/`，每个节点一个文件，使用 frontmatter + 可读 Markdown 正文。`graph/index.md` 负责将 ID 映射到文件路径，由工具机械维护，不承载世界事实。
- ID 稳定且不得复用：`event_<n>`、`entity_<slug>`、`anchor_<n>`。每个新 ID 都必须注册到 `graph/index.md`。
- 关系存放在起点节点的 frontmatter `relations:` 列表中；每条关系都有独立的 `sources`，因此节点和边的 provenance 可以分别追踪。
- MVP 关系词汇：`causes`、`before`、`after`、`contains`、`located_in`、`knows`、`member_of`、`owns`、`requires`、`participates_in`。需要新增关系类型时，先向用户说明原因并确认。
- Event 使用 `previous` / `next` 链表示顺序；`time.approximate` 只用于同一分支内排序。Graph 内部时间线属于世界结构，不等同于 Git 分支。
- Anchor 是带有 `paradox_policy` 的 Event（默认 `reject`）。PR 中涉及 Anchor 的冲突应明确指出，由用户决定是否接受。

## 根据创作讨论准备 PR

当用户要求根据当前讨论准备或创建 PR 时：

1. 检查相关 Ideas、Graph 节点和正文证据。
2. 将值得保留的讨论结论、设定想法和未决方向整理进 `ideas/`。不要保存原始对话；优先更新已有 Idea，避免重复创建。
3. 识别由讨论产生且证据足够的 Graph 更新。
4. 更新对应 Graph 节点和 `graph/index.md`，并保留指向相关 `idea` 或 `draft` 路径的 provenance。
5. PR 分支上的 Graph 修改不是最终 Canon。只有用户将 PR 合入 `main` 后，才成为主线 Canon。
6. 用户要求时创建 Git commit 和 PR。PR 描述应说明概念变化以及重要的一致性注意事项。

不再设置独立的 Semantic Review。PR 本身就是 Review 边界：用户可以检查完整 diff、提出修改意见、让 AI 修改分支，或自己合入。

## 审查 PR 的世界一致性

当用户要求 AI Review 一个 PR 时，必须以 **当前 `main`** 的 Graph 和 Draft 作为基准，而不是只根据 PR 分支本身进行判断。

开始审查前，先确保本地已获得最新的 `origin/main` 基线（例如执行 `git fetch origin main`）。以 `origin/main` 中的 Graph 和 Draft 作为当前 Canon 基线：先读取 `origin/main:graph/index.md`，再按需读取其中相关节点文件；同时读取 `origin/main` 中与变更相关的 Draft 和索引。然后将这些内容与 PR 分支上的拟议变更进行比较。不要把 PR 分支中已经修改过的 Graph 或 Draft 当作审查基线。

检查：

- 是否与现有 Graph Canon 冲突；
- 是否与正文已经明确建立的事实冲突；
- 时间线是否一致；
- Entity 的身份、状态、行为、归属和关系是否合理；
- Event 的因果关系和前置条件是否成立；
- 是否符合已经建立的世界规则；
- 新增 Graph 结构是否忠实反映其 Idea / Draft 来源；
- 是否引入逻辑矛盾或缺乏来源支持的事实。

将结果区分为：明确矛盾、潜在风险、证据不足。AI Review 只是审查意见，不自动批准、拒绝或合并 PR。

## 审查章节

当用户要求检查指定章节是否存在问题时：

1. 确定目标章节及其所属书目。若用户直接提供正文，则以提供的正文为目标。如果项目有多本书且无法确定所属书目，应询问用户。
2. 读取该书的索引（`draft/<book>/index.md`，单本书项目则使用 `draft_index`）确定章节顺序。默认只读取目标章节之前的章节。如果索引缺失或不完整，则使用自然文件名顺序，并说明不确定性。
3. 从目标章节提取实体、关系、知识、地点、物品、伤势、资源和事件。
4. 搜索相关 Graph 节点、Idea 和前文。对强匹配的 Graph 节点展开一跳关系。
5. 检查世界规则、人物身份与知识范围、关系、OOC、时间线、移动、地点连续性、物品归属、身体状态、资源、伏笔和因果。与 Graph Canon 冲突属于明确问题，需要作者决定。
6. 将发现分为“明确问题”“潜在风险”“证据不足”。
7. 给出目标章节证据以及冲突或支持它的项目证据。不要把纯粹的文风偏好当成一致性问题。

返回紧凑结构：

```markdown
# 章节审查
## 摘要
## 明确问题
### 问题
- 严重程度：
- 章节证据：
- 项目证据：
- 原因：
- 建议处理：
## 潜在风险
## 证据不足
```

空章节不输出。除非用户明确要求，否则不要读取目标章节之后的内容。

## 维护 Ideas

当当前对话产生值得长期保留的创作结论时，在用户要求保存、记录、总结或准备 PR 时更新相关 Idea。优先更新已有 Idea，而不是创建重复文件。

一个有用的 Idea 总结可以包含：

- **背景** — 产生这个想法或结论的原因；
- **内容** — 当前理解；
- **方案** — 重要的已否定或仍在比较的可能性；
- **未决问题** — 尚未决定的内容。

不要擅自把讨论变成 Canon。如果用户没有要求准备 PR 或其他 Graph 变更，就保持 Graph 不变。
