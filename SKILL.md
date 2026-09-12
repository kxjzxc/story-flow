---
name: story-flow
description: Initialize daoverse StoryFlow projects, retrieve context from ideas, drafts, and the world graph, follow wikilinks and backlinks, review chapters against graph canon and earlier manuscript, extract graph updates with provenance, maintain shared ideas from creative discussions, and review pull requests for world consistency. Use for story project setup, story questions, chapter consistency or OOC checks, timeline and continuity analysis, graph extraction, idea capture and organization, and requested PR reviews.
---

# StoryFlow

Use Markdown files as the story source. Retrieve evidence before answering. Ideas are a shared
creative workspace: the user and AI may edit them, but they are not canon. Draft and graph are
canon and must only enter `main` through the user's Git workflow.

## Data model

StoryFlow keeps three kinds of data:

- `idea` — creative material maintained by the user and AI; not canon.
- `draft` — narrative canon maintained by the author.
- `graph` — structured world canon: events, entities, anchors, and relations with provenance.

These are data type names, not directory paths. Ideas live under `ideas/`, and `draft`/`graph`
types live under `draft/`/`graph/`.

```text
idea  → 创作过程中正在形成什么
draft → 作者已经写了什么
graph → 当前世界是什么
```

An Idea may be an inspiration, a conclusion from discussion, a possible setting, an open
question, or other useful creative material. It can be edited directly by either the user or AI.
AI should primarily preserve the useful conclusions of the current conversation by summarizing
them into the relevant Idea rather than storing raw conversations as files.

## Locate the project

1. Find the nearest `STORYFLOW.md` at or above the working file.
2. Treat its directory as the project boundary. Do not follow links outside it.
3. Read the `storyflow` frontmatter for `idea_roots`, `draft_roots`, `draft_index`,
   `graph_root`, and `graph_index`.
4. Use `ideas`, `draft`, `draft/index.md`, `graph`, and `graph/index.md` when a field is absent.
5. Do not invent a conversation archive. The active chat is the creative process; preserve useful
   conclusions in `ideas/` when appropriate.

Each book is a directory under a draft root with its own `index.md` listing its chapters; the
draft root's `index.md` lists the books. A draft root that lists chapters directly instead of
book directories is a single-book project.

When no manifest exists, ask the user for a project root or offer to initialize one with:

```bash
python scripts/init_project.py PROJECT_PATH --title "Story title"
```

The initializer creates the Markdown project files and installs this skill into
`PROJECT_PATH/.codex/skills/story-flow/` by default. Use `--no-install-skill` only when the
user asks for a pure Markdown template.

## Enforce access boundaries

- Read idea, draft, and graph files only as required by the active task.
- Ideas are non-canon working material. Do not present an Idea as an established world fact.
- The user and AI may both edit ideas. When the user asks to preserve discussion conclusions,
  summarize them into the relevant Idea instead of creating a conversation record.
- Graph is canon. AI may update graph files when the user explicitly asks to prepare a PR, but
  the changes do not become Canon on `main` until the user merges the PR.
- Never invent graph facts without provenance. Every node and relation must cite a source path in
  `draft` or `idea`.
- Do not edit draft or its indexes. Produce reports and proposed wording in the response instead,
  unless a future workflow explicitly grants draft editing.
- AI must never merge a PR on behalf of the user.

## Retrieve story context

1. Extract names, aliases, node ids, locations, organizations, events, objects, rules, and
   distinctive phrases from the request.
2. Resolve explicit node ids through `graph_index` first: read the node file, expand its
   `relations` by one hop, then read cited sources when needed.
3. Search configured idea and draft roots. Prefer exact title, frontmatter alias, and exact phrase
   matches before broad keyword matches.
4. Parse `[[note]]`, `[[note|label]]`, and relative Markdown links from strong matches.
5. Expand direct links and backlinks by one hop only. Resolve by frontmatter `storyflow.id`,
   relative path, filename, then alias. Report ambiguous links instead of guessing.
6. Rank explicit files above index entries, index entries above exact matches, exact matches above
   linked notes, and linked notes above broad keyword matches.
7. Answer with paths and headings for factual claims. Separate project evidence from inference.

Do not use embeddings or build a persistent index. Use file listing, text search, links, and
 targeted reads.

## Graph model

- Nodes live under `graph/nodes/{event,entity,anchor}/`, one file per node, as frontmatter plus a
  readable Markdown body. `graph/index.md` maps ids to paths and is maintained mechanically; it
  carries no world facts.
- Ids are stable and never reused: `event_<n>`, `entity_<slug>`, `anchor_<n>`. Every new id is
  registered in `graph/index.md`.
- Relations are stored in the `from` node's frontmatter `relations:` list; each relation carries
  its own `sources`, so node and edge provenance are independent.
- MVP relation vocabulary: `causes`, `before`, `after`, `contains`, `located_in`, `knows`,
  `member_of`, `owns`, `requires`, `participates_in`. A new relation type must be proposed to
  the user with a reason and is usable only after confirmation.
- Events use `previous`/`next` chains for order; `time.approximate` only sorts within a branch.
  Graph-internal timelines are world structure and are not the same as Git branches.
- Anchors are events with `paradox_policy` (default `reject`). Conflicts with anchors should be
  highlighted clearly in PR review; the user decides whether to accept the change.

## Prepare a PR from a creative discussion

Use this workflow when the user asks to prepare or create a PR based on the current discussion.

1. Review the relevant existing Ideas, Graph nodes, and manuscript evidence.
2. Update or create the relevant Idea files with useful conclusions from the discussion. Do not
   preserve raw dialogue; summarize it into durable creative material.
3. Identify Graph changes that follow from the discussion and have enough evidence to be recorded.
4. Update the corresponding Graph nodes and `graph/index.md`, preserving provenance to the
   relevant `idea` or `draft` path.
5. Do not treat the changes as final Canon merely because they exist on the PR branch. Canon is
   the state of `main` after the user's merge.
6. Create a Git commit and PR when requested. The PR should explain the conceptual changes and
   any important consistency considerations.

There is no separate Semantic Review gate. The PR is the review boundary: the user can inspect
the complete diff, request changes, ask AI to revise the branch, or merge it themselves.

## Review a PR for world consistency

When the user asks AI to review a PR, evaluate the proposed changes against the **current `main`**
Graph and Draft, not against assumptions from the PR branch alone.

Check:

- conflicts with existing Graph canon;
- conflicts with facts explicitly established in the manuscript;
- timeline consistency;
- entity identity, state, behavior, ownership, and relationships;
- event causality and prerequisites;
- consistency with established world rules;
- whether the new Graph structure faithfully represents its Idea/Draft sources;
- whether the change introduces a logical contradiction or unsupported fact.

Separate findings into clear contradictions, possible risks, and insufficient evidence. AI review is
advisory: it does not approve, reject, or merge the PR automatically.

## Review a chapter

Use this workflow when the user asks whether a specified or pasted chapter has problems.

1. Identify the target chapter and its book. Treat pasted prose as the target when no path is
   given. If the project has multiple books and the book is ambiguous, ask which book the chapter
   belongs to.
2. Read the book's index (`draft/<book>/index.md`, or `draft_index` for a single-book project) to
   determine chapter order. Read only chapters before the target by default. If the index is
   missing or incomplete, use natural filename order and disclose the uncertainty.
3. Extract entities, relationships, knowledge, locations, objects, injuries, resources, and events
   from the target.
4. Search relevant graph nodes, idea notes, and earlier chapters for those elements. Expand strong
   graph matches by one relation hop.
5. Check world rules, character identity and knowledge, relationships, OOC behavior, timeline,
   travel, location continuity, object ownership, physical state, resources, foreshadowing, and
   causality. Contradictions with graph canon are clear issues and need an author decision.
6. Classify each finding as `clear issue`, `possible risk`, or `insufficient evidence`.
7. Cite target evidence and conflicting or supporting source evidence. Do not report a style
   preference as a consistency problem.

Return this compact structure:

```markdown
# Chapter review
## Summary
## Clear issues
### Finding
- Severity:
- Chapter evidence:
- Project evidence:
- Reason:
- Suggested resolution:
## Possible risks
## Insufficient evidence
```

Omit empty sections. Do not read later chapters unless the user explicitly requests it.

## Maintain Ideas

When the current conversation produces durable creative conclusions, update the relevant Idea when
asked to save, record, summarize, or prepare a PR. Prefer updating an existing Idea over creating
duplicates.

A useful Idea summary may contain:

- **Context** — what prompted the idea or conclusion;
- **Content** — the current understanding;
- **Alternatives** — important rejected or unresolved possibilities;
- **Open questions** — what remains undecided.

Do not silently turn discussion into Canon. If the user has not asked to prepare a PR or otherwise
record a Graph change, keep Graph untouched.
