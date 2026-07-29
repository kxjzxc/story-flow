# StoryFlow

StoryFlow V1 不是小说编辑器，不是笔记软件，也不是 AI 写作产品。

它是一套极小的 Codex Skill + Markdown 项目模板，用来帮助作者在本地 Markdown 仓库里和 AI 协作创作。

它支持：

- 检索设定库和历史正文
- 基于双链和反向链接构建小范围上下文
- 根据已有设定和前文审查指定章节
- 根据用户提供的新正文生成设定更新报告
- 记录每次 StoryFlow 对话
- 仅在用户明确要求时总结对话

核心原则：

> StoryFlow 管理的是创作过程，而不是创作结果。

设定和正文仍然属于作者自己的 Markdown 仓库。Skill 可以读取、分析、报告，但不能擅自修改正文、设定或 Canon 内容。

## 当前实现了什么

这个仓库目前实现的是一个 Skill 包，不是独立应用。

```text
story-flow/
  SKILL.md                         # StoryFlow 的 AI 工作流规则
  agents/openai.yaml               # Skill 展示信息
  assets/project-template/
    STORYFLOW.md                   # 项目配置文件模板
    setting/index.md               # 设定库入口
    draft/index.md                 # 正文顺序入口
  scripts/
    init_project.py                # 初始化 StoryFlow Markdown 项目
    log_conversation.py            # 安全追加对话记录
  tests/                           # 脚本测试
```

最重要的是 `SKILL.md`。它定义了 AI 在 StoryFlow 项目里应该如何查找项目、如何读取上下文、哪些文件默认不能读、以及章节审查和设定更新报告应该如何输出。

## 项目目录

使用初始化脚本后，一个故事项目会得到这样的结构：

```text
my-story/
  STORYFLOW.md
  .codex/
    skills/
      story-flow/
        SKILL.md
        assets/
        scripts/
  setting/
    index.md
  draft/
    index.md
  _storyflow/
    conversations/
```

`STORYFLOW.md` 是项目配置文件。它声明设定库、正文目录、正文顺序文件和对话记录目录的位置。

`.codex/skills/story-flow/` 是项目本地 Skill。初始化脚本默认会把 StoryFlow Skill 拷贝到这里。之后在 `my-story/` 目录里打开 Codex，或把这个目录作为工作空间交给 Codex，就可以通过 `$story-flow` 调用这套工作流。

`setting/` 是扁平的设定库入口，不建议用多层文件夹维护世界观分类。设定之间应该通过双链连接，例如 `[[角色-林青]]`、`[[旧王都]]`、`[[月潮规则]]`。

`draft/` 存放正文。`draft/index.md` 用来列出章节阅读顺序。这样 AI 审查第 8 章时，可以只参考第 1 到第 7 章，而不会误用后文剧透。

`_storyflow/conversations/` 存放对话记录。这个目录默认只写不读。AI 不会把历史对话当成普通故事上下文，除非用户明确要求检索、查看或总结历史对话。

## 初始化项目

```bash
./scripts/init_project.py /path/to/my-story --title "故事名称"
```

初始化脚本只创建缺失文件，不会覆盖已有文件。它默认也会把 StoryFlow Skill 安装到目标项目的 `.codex/skills/story-flow/`。

如果只想生成纯 Markdown 结构，不拷贝 Skill：

```bash
./scripts/init_project.py /path/to/my-story --title "故事名称" --no-install-skill
```

初始化完成后，在故事项目目录中可以这样调用：

```text
$story-flow 帮我检查 draft/chapter08.md 是否和前文、设定冲突
```

或者：

```text
$story-flow 根据这段新正文，检查设定库是否需要更新
```

## AI 如何检索上下文

普通故事问题只会检索 `STORYFLOW.md` 配置里的设定目录和正文目录。

检索依据包括：

- 精确名称、别名、标题和关键短语
- Front Matter 里的字段
- `[[双链]]`、`[[双链|显示名]]`
- 相对 Markdown 链接
- 一跳范围内的正向链接和反向链接

V1 不建立数据库，不维护 embedding 索引，也不做持久缓存。

AI 回答事实性问题时，应该引用 Markdown 路径和标题，方便作者核查来源。

## 支持的工作流

章节审查：

用户指定某一章，或直接粘贴正文后，AI 会根据已有设定和前文检查潜在问题，例如时间线、人物知识、OOC、地点连续性、物品归属、因果关系等。结果会区分为明确问题、可能风险和证据不足。

设定更新报告：

用户提供新正文后，AI 会检查其中是否出现值得沉淀到设定库的内容，并生成报告。报告只给出建议新增、建议更新、冲突和不值得记录的内容，不会直接修改设定文件。

对话记录：

StoryFlow 对话可以被记录到 `_storyflow/conversations/`。记录内容只包含用户可见的消息和助手最终回复，不包含隐藏提示词、推理过程、工具输出或检索到但未出现在回复里的材料。

对话总结：

只有当用户明确要求总结对话时，AI 才会总结当前或指定历史对话。对话总结仍然只是创作过程记录，不等于设定或 Canon。

## 手动记录对话

创建对话记录文件：

```bash
./scripts/log_conversation.py start \
  --project /path/to/my-story \
  --conversation-root _storyflow/conversations \
  --title "讨论第一章问题"
```

追加一条可见消息：

```bash
./scripts/log_conversation.py append \
  --session /path/to/session.md \
  --role user \
  --content-file message.txt
```

追加一份总结：

```bash
./scripts/log_conversation.py summarize \
  --session /path/to/session.md \
  --content-file summary.txt
```

`log_conversation.py` 故意不提供读取命令，避免对话记录被默认当成上下文使用。

## 非目标

StoryFlow V1 不做：

- Markdown 编辑器
- 笔记管理
- 云同步
- Git 管理
- 自动提升 Canon
- 自动修改正文或设定
- 模型托管
- embedding 或语义搜索

它刻意保持很小：一套文件约定，加上一个让 AI 更好遵守这些约定的 Skill。

## 验证

```bash
python3 -B -m unittest discover -s tests -v
```
