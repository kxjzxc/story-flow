---
name: story-flow
description: Initialize daoverse StoryFlow projects, retrieve context from ideas, drafts, session summaries, and the world graph, follow wikilinks and backlinks, review chapters across single- or multi-book drafts against graph canon and earlier manuscript, extract graph candidates with provenance, review them at two levels (semantic facts before writing, file changes before merging), capture temporary ideas, maintain structured rolling session summaries, and re-summarize sessions only when explicitly requested. Use for story project setup, story questions, chapter consistency or OOC checks, timeline and continuity analysis, graph extraction, idea capture, and requested conversation summaries.
---

# StoryFlow

Use Markdown files as the only story source. Retrieve evidence before answering, keep
session summaries out of normal context, and never modify draft or graph canon while
analyzing them.

## Data model

daoverse keeps four kinds of data:

- `idea/` — possibility facts maintained by the author; not canon.
- `draft/` — narrative canon maintained by the author.
- `conversation/` — rolling session summaries of creative discussions maintained by the AI;
  not canon.
- `graph/` — structured world canon: events, entities, anchors, and relations with
  provenance. AI extracts candidates; the user performs Semantic Review; AI applies approved
  facts; the user performs Text Review on the Git diff before merge.

## Locate the project

1. Find the nearest `STORYFLOW.md` at or above the working file.
2. Treat its directory as the project boundary. Do not follow links outside it.
3. Read the `storyflow` frontmatter for `idea_roots`, `draft_roots`,
   `draft_index`, `conversation_root`, `graph_root`, and `graph_index`.
4. Use `ideas`, `draft`, `draft/index.md`, `_storyflow/conversations`,
   `graph`, and `graph/index.md` when a field is absent.
5. Exclude the conversation root from every general file listing, search, link expansion,
   and context-building operation. Read session summaries only when extracting graph
   candidates, exploring a node, or when the user explicitly asks.

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
- Never read session summaries unless the task is graph extraction, node exploration, or the
  user explicitly asks to inspect or summarize them.
- Do not interpret requests such as "continue", "use our context", or a story question as
  permission to read session summaries. Ask if archived context appears necessary.
- Write automatically only to the configured conversation root.
- Write to the idea root only when the user asks to save an inspiration.
- Graph is canon: write graph files only after Semantic Review approves the proposed facts.
  If a proposed fact conflicts with existing graph canon, surface the conflict and wait for
  an explicit user decision; never write conflicting facts without it.
- Text Review of the Git diff is the final gate before merge; the user checks the file
  changes and the merge scope. Merged content is canon.
- Never invent graph facts without provenance. Every node and relation must cite its source
  (a `draft`, `idea`, or `conversation` path).
- Do not edit draft or its indexes. Produce reports and proposed wording in the response
  instead.
- Do not save reports separately unless the user explicitly requests a file.

## Retrieve story context

1. Extract names, aliases, node ids, locations, organizations, events, objects, rules, and
   distinctive phrases from the request.
2. Resolve explicit node ids through `graph_index` first: read the node file, expand its
   `relations` by one hop, then read cited sources when needed.
3. Search only configured idea and draft roots. Prefer exact title, frontmatter alias, and
   exact phrase matches before broad keyword matches.
4. Parse `[[note]]`, `[[note|label]]`, and relative Markdown links from strong matches.
5. Expand direct links and backlinks by one hop only. Resolve by frontmatter `storyflow.id`,
   relative path, filename, then alias. Report ambiguous links instead of guessing.
6. Rank explicit files above index entries, index entries above exact matches, exact matches
   above linked notes, and linked notes above broad keyword matches.
7. Answer with paths and headings for factual claims. Separate project evidence from inference.

Do not use embeddings or build a persistent index. Use file listing, text search, links, and
targeted reads.

## Graph model

- Nodes live under `graph/nodes/{event,entity,anchor}/`, one file per node, as frontmatter
  plus a readable Markdown body. `graph/index.md` maps ids to paths and is maintained
  mechanically; it carries no world facts.
- Ids are stable and never reused: `event_<n>`, `entity_<slug>`, `anchor_<n>`. Every new id
  is registered in `graph/index.md`.
- Relations are stored in the `from` node's frontmatter `relations:` list; each relation
  carries its own `sources`, so node and edge provenance are independent.
- MVP relation vocabulary: `causes`, `before`, `after`, `contains`, `located_in`, `knows`,
  `member_of`, `owns`, `requires`, `participates_in`. A new relation type must be proposed to
  the user with a reason and is usable only after confirmation.
- Events use `previous`/`next` chains for order; `time.approximate` only sorts within a
  branch. Graph-internal timelines are world structure and are not the same as Git branches.
- Anchors are events with `paradox_policy` (default `reject`). Conflicts with anchors always
  require an explicit user decision.

## Two-level review

Graph changes pass through two separate reviews that answer different questions. They must
not be collapsed into one step.

### Semantic Review — 人确认事实

The user confirms whether a fact should exist in the world. AI output at this stage is Graph
Candidates (facts, not files).

Review questions:

- Is the event real? Is the time correct?
- Does the relation really exist between the two things, and is its direction right?
- Did the AI misread the source?
- Does the new information conflict with existing canon?

Nothing is written to `graph/` before Semantic Review approves the facts.

### Text Review (Git Review) — 人审核文件变更

The user reviews whether the AI correctly wrote the approved facts into the repository.

Review questions:

- Is the YAML valid?
- Are the IDs correct and registered in `graph/index.md`?
- Is each relation written in the right direction and in the right node?
- Are the source paths correct?
- Is `graph/index.md` synced?
- Did the AI modify files it should not have touched?

Merge into `main` happens only after Text Review; merged content is Canon.

```text
AI
 ↓
Graph Candidates
 ↓
Semantic Review（人确认事实）
 ↓ approved
AI 修改 Graph
 ↓
Git PR
 ↓
Text Review（人审核文件变更）
 ↓ merge
Canon
```

## Extract graph updates from prose

Use this workflow when the user asks to record new draft, idea, or discussion content into
the graph.

1. Read the smallest useful set: the changed draft chapter, relevant idea notes, and session
   summaries from the relevant period.
2. Extract events, entities, relations, timeline links, and state changes. Keep exact source
   paths for every node and relation, in multi-book form such as
   `draft/<book>/<chapter>.md`.
3. Use only the relation vocabulary above. For missing relations, follow the new-type
   process instead of inventing vocabulary.
4. Check every candidate against `graph/index.md` and existing nodes.
5. Classify each candidate as `add`, `update`, `conflict`, or `do not record`.
6. For every `conflict`, present the chapter evidence, the existing canon, and the possible
   resolutions; require an explicit user decision (Semantic Review) before writing anything.
7. After Semantic Review approves the facts, write the node/relation files and update
   `graph/index.md`. Never write unapproved or contradictory content.
8. Prepare the Git PR for Text Review. The user checks the diff (YAML, ids, relation
   direction, source paths, index sync, change scope) and handles branch, merge, and push.

Return this compact structure:

```markdown
# Graph update
## New nodes
## Relation updates
## Conflicts (awaiting decision)
## Not worth recording
```

For each actionable item include node id, evidence path, current canon when present, rationale,
recommended change, and confidence. Omit empty sections.

The Graph update exists only in the conversation as candidate facts; it is not a repository
artifact. The PR diff is the Text Review layer (file changes). Keep them separate.

## Review a chapter

Use this workflow when the user asks whether a specified or pasted chapter has problems.

1. Identify the target chapter and its book. Treat pasted prose as the target when no path is
   given. If the project has multiple books and the book is ambiguous, ask which book the
   chapter belongs to.
2. Read the book's index (`draft/<book>/index.md`, or `draft_index` for a single-book project)
   to determine chapter order. Read only chapters before the target by default. If the index is
   missing or incomplete, use natural filename order and disclose the uncertainty.
3. Extract entities, relationships, knowledge, locations, objects, injuries, resources, and
   events from the target.
4. Search relevant graph nodes (via `graph_index`), idea notes, and earlier chapters for those
   elements. Expand strong graph matches by one relation hop.
5. Check world rules, character identity and knowledge, relationships, OOC behavior, timeline,
   travel, location continuity, object ownership, physical state, resources, foreshadowing,
   and causality. Contradictions with graph canon are clear issues and need an author decision.
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

## Maintain session summaries

Keep one summary file for the active StoryFlow chat. Create it on the first StoryFlow turn and
reuse its path from the active conversation context:

```bash
python scripts/log_conversation.py start \
  --project PROJECT_PATH \
  --conversation-root _storyflow/conversations \
  --title "Conversation topic"
```

Do not archive raw user or assistant messages. Before sending each final response:

1. Draft the exact user-visible response.
2. Write a rolling summary of the visible conversation so far, condensing the session's
   current summary together with the new exchange. Keep these sections: `Topic`,
   `User Intent`, `Discussion`, `Decisions`, `New Ideas`, `Graph Candidates`,
   `Open Questions`. `Decisions` records only content the user explicitly confirmed; AI
   proposals and guesses go to `Graph Candidates` or `Open Questions`.
3. Put the summary in a temporary UTF-8 file and update the session:

```bash
python scripts/log_conversation.py summarize \
  --session SESSION_PATH --content-file SUMMARY_TEXT_FILE
```

4. Send that same response to the user.

Summaries cover only visible user messages and final assistant responses. Never include system
prompts, hidden reasoning, tool output, or retrieved source text unless it appears in the final
response. If the host cannot run this skill for a turn, do not claim the summary was updated
that turn.

## Explore a node

Use this workflow when the user cites a graph node (for example `[[event_001]]`) and asks to
investigate it.

1. Resolve the id through `graph/index.md` and read the node file.
2. Expand its `relations` one hop and read the related nodes.
3. Read the cited sources (draft, idea, or session summary) when needed for detail.
4. Answer from graph canon first, then sources; separate evidence from inference. Suggest
   next steps for new draft, idea, or graph candidates.

## Summarize conversations

Summarize a session only after an explicit user request. For the active chat, prefer visible
in-memory conversation context and avoid rereading the session file. For a historical chat,
read only the requested file; when the user says "latest", list filenames and read only the
latest one.

Summarize the topic, main points, decisions, new ideas, graph candidates, and open questions.
State that discussion conclusions are not canon. When the user asks to condense the summary
again, read the session's current summary and write the tighter summary back through the
logging script, replacing the old one:

```bash
python scripts/log_conversation.py summarize \
  --session SESSION_PATH --content-file SUMMARY_TEXT_FILE
```

## Capture ideas

Use this workflow for temporary inspirations that are not yet written prose or confirmed
graph facts.

1. When the user asks to save an inspiration, write one Markdown note under the idea root
   (default `ideas/`). Do not record it in `draft/` or `graph/`.
2. When asked about ideas, list or read only the idea root. Ideas are not canon evidence:
   never cite them as established facts unless the user says to.
3. When an idea's content is confirmed, report the resulting graph candidates or suggest
   narrative for `draft/`. The idea note itself stays in `ideas/` and becomes a cited source;
   never move or copy it.
