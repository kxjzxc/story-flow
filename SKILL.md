---
name: story-flow
description: Initialize StoryFlow Markdown projects, retrieve context from story settings and manuscripts, follow wikilinks and backlinks, archive StoryFlow conversations without using them as context, summarize conversations only when explicitly requested, review requested chapters against established settings and earlier manuscript, and report setting updates suggested by user-provided prose. Use for StoryFlow projects, story project setup, story questions, chapter consistency or OOC checks, timeline and continuity analysis, setting update reports, and requested conversation summaries.
---

# StoryFlow

Use Markdown files as the only story source. Retrieve evidence before answering, keep
conversation archives out of normal context, and never modify settings or manuscript while
analyzing them.

## Locate the project

1. Find the nearest `STORYFLOW.md` at or above the working file.
2. Treat its directory as the project boundary. Do not follow links outside it.
3. Read the `storyflow` frontmatter for `setting_roots`, `draft_roots`,
   `draft_index`, and `conversation_root`.
4. Use `setting`, `draft`, `draft/index.md`, and `_storyflow/conversations` when a
   field is absent.
5. Exclude the conversation root from every general file listing, search, link expansion,
   and context-building operation.

When no manifest exists, ask the user for a project root or offer to initialize one with:

```bash
python scripts/init_project.py PROJECT_PATH --title "Story title"
```

The initializer creates the Markdown project files and installs this skill into
`PROJECT_PATH/.codex/skills/story-flow/` by default. Use `--no-install-skill` only when the
user asks for a pure Markdown template.

## Enforce access boundaries

- Read settings and manuscript only as required by the active task.
- Never read conversation files unless the user explicitly asks to inspect, search, or
  summarize conversation history.
- Do not interpret requests such as "continue", "use our context", or a story question as
  permission to read archived conversations. Ask if archived context appears necessary.
- Write automatically only to the configured conversation root.
- Do not edit settings, manuscript, or their indexes. Produce reports and proposed wording in
  the response instead.
- Do not save reports separately unless the user explicitly requests a file.

## Retrieve story context

1. Extract names, aliases, locations, organizations, events, objects, rules, and distinctive
   phrases from the request.
2. Search only configured setting and draft roots. Prefer exact title, frontmatter alias, and
   exact phrase matches before broad keyword matches.
3. Read the smallest useful set of matching sections rather than whole files.
4. Parse `[[note]]`, `[[note|label]]`, and relative Markdown links from strong matches.
5. Expand direct links and backlinks by one hop only. Resolve by frontmatter `storyflow.id`,
   relative path, filename, then alias. Report ambiguous links instead of guessing.
6. Rank explicit files above exact matches, exact matches above linked notes, and linked notes
   above broad keyword matches.
7. Answer with paths and headings for factual claims. Separate project evidence from inference.

Do not use embeddings or build a persistent index. Use file listing, text search, links, and
targeted reads.

## Review a chapter

Use this workflow when the user asks whether a specified or pasted chapter has problems.

1. Identify the target chapter. Treat pasted prose as the target when no path is given.
2. Read `draft_index` to determine chapter order. Read only chapters before the target by
   default. If the index is missing or incomplete, use natural filename order and disclose the
   uncertainty.
3. Extract entities, relationships, knowledge, locations, objects, injuries, resources, and
   events from the target.
4. Search relevant setting notes and earlier chapters for those elements. Expand strong
   setting matches by one graph hop.
5. Check world rules, character identity and knowledge, relationships, OOC behavior, timeline,
   travel, location continuity, object ownership, physical state, resources, foreshadowing,
   and causality.
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

## Report setting updates from prose

Use this workflow when the user provides prose and asks what the setting library may need to
record or change.

1. Extract durable facts about characters, relationships, locations, organizations, world
   rules, events, objects, and long-lived state changes.
2. Ignore transient actions, ordinary scenery, rhetoric, unconfirmed narrator speculation,
   and details unlikely to constrain future writing.
3. Search only setting roots for matching notes, then expand strong matches by one graph hop.
   Do not read prior manuscript or conversations unless explicitly requested.
4. Compare prose evidence with current setting evidence.
5. Classify candidates as `add`, `update`, `conflict`, or `do not record`.
6. For state changes, preserve the old state as history and recommend adding the transition;
   do not recommend blindly replacing it.
7. Treat every item as a candidate for author review. Never apply it.

Return this compact structure:

```markdown
# Setting update report
## Suggested additions
## Suggested updates
## Conflicts
## Not worth recording
```

For each actionable item include the target note, prose evidence, current setting evidence when
present, rationale, recommended change, and confidence. Omit empty sections.

## Archive conversations

Keep one archive file for the active StoryFlow chat. Create it on the first StoryFlow turn and
reuse its path from the active conversation context:

```bash
python scripts/log_conversation.py start \
  --project PROJECT_PATH \
  --conversation-root _storyflow/conversations \
  --title "Conversation topic"
```

Before sending each final response:

1. Draft the exact user-visible response.
2. Put the current user message in a temporary UTF-8 file and append it with role `user`.
3. Put the exact final response in another temporary UTF-8 file and append it with role
   `assistant`.
4. Send that same response to the user.

```bash
python scripts/log_conversation.py append \
  --session SESSION_PATH --role user --content-file USER_TEXT_FILE
python scripts/log_conversation.py append \
  --session SESSION_PATH --role assistant --content-file RESPONSE_TEXT_FILE
```

Archive only visible user messages and final assistant responses. Never archive system prompts,
hidden reasoning, tool output, or retrieved source text unless it appears in the final response.
If the host cannot run this skill for a turn, do not claim that turn was archived.

## Summarize conversations

Summarize an archive only after an explicit user request. For the active chat, prefer visible
in-memory conversation context and avoid rereading the archive. For a historical chat, read only
the requested file; when the user says "latest", list filenames and read only the latest one.

Summarize the topic, main points, conclusions, open questions, and possible next steps. State
that discussion conclusions are not story settings. Append the user-visible summary to the
session without reading it through the logging script:

```bash
python scripts/log_conversation.py summarize \
  --session SESSION_PATH --content-file SUMMARY_TEXT_FILE
```
