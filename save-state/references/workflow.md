# save-state — full workflow (default mode and `--end`)

Read by `SKILL.md` for the two modes that have the context budget for it. `--quick` never reads this file.

The two modes share Phases 1 to 5. They differ on the depth of the doc pass (Phase 3), on who reads the state file next (Phase 4), and on how the turn ends (Phase 6).

| | Default | `--end` |
| --- | --- | --- |
| Why | a `/compact` is coming | the session is over, the user closes it |
| Doc pass | scoped, sections only | every affected doc read in full |
| Next reader of the state file | the same session, compacted (keeps a summary) | a brand-new session (knows nothing) |
| Ends with | Block A + Block B | report + one resume line |

## Context budget

**Default mode runs at ~300k tokens.** Burning 30k tokens to prepare a compaction defeats the purpose.

- No full-repo exploration. No `git log`, no broad globs, no reading files you have no intention of editing.
- Locating is cheap, reading is not. `ls`, `find docs -name '*.md'` and a targeted `grep` for a stale claim are fine. Reading a 600-line doc to confirm it's unaffected is not.
- A file already read in full this session counts as read, unless something changed it since.
- On a long file you're editing, re-read the section, not the file.

**`--end` has no compaction pending.** The budget loosens: every doc that describes something the session touched gets read in full, because the next session will trust it blindly. It still isn't a full-repo audit. That's `/doc-sync`: if the user wants every doc checked, say so in one line.

## Phase 1 — What this session actually changed

Write the change list from what you already know about the session, plus two cheap commands:

```bash
git status --short
git diff --stat
```

Cover every category. Write "none" explicitly where there's nothing — that proves you considered it:

- **Code & structure**: new/deleted/moved modules, refactors
- **Public surface**: functions, endpoints, props, types, CLI flags
- **Data model**: schema, migrations, new fields
- **Config**: env vars, config keys, feature flags, dependencies
- **Commands & workflows**: scripts, build/test/deploy steps
- **Behavior**: user-visible changes a doc might describe
- **Decisions**: choices made this session, each with the reason it beat the alternative
- **Traps**: gotchas discovered that would cost real time to rediscover
- **Task progress**: what got done against the plan, what's still open

This list is the input to everything that follows. A file only gets touched in Phase 3 if something here made it false.

## Phase 2 — Targeted inventory

For each of the four buckets, list the candidate files with a one-line reason. A file is a candidate when Phase 1 plausibly contradicts it, or when it describes the area the session touched.

**Bucket 1 — Project docs.** `README.md`, `CLAUDE.md`, `docs/*.md`, package-level READMEs. Locate them cheaply:

```bash
ls README.md CLAUDE.md 2>/dev/null
find docs -type f -name "*.md" 2>/dev/null | sort
```

Then filter against Phase 1. `CLAUDE.md` deserves a second look — it's written for future sessions, which is exactly what's about to happen.

**Bucket 2 — Working files.** `tasks/todo.md` (check off what shipped, add what emerged), `tasks/lessons.md` (any correction the user made this session), plan files referenced during the session (check `~/.claude/plans/` if a plan drove the work).

**Bucket 3 — The state file.** `.claude/session-state.md`. Always a target, every run. Phase 4 handles it. If the previous file has a "Docs to update" section (left by a `--quick` run), every path listed there becomes a Bucket 1 candidate.

**Bucket 4 — Claude memory.** `~/.claude/projects/<project-slug>/memory/`. Only if a **durable** fact emerged — a user preference, a constraint, an external reference that will still matter in three weeks. Not session narrative, not anything the repo already records. Follow the memory rules in the system prompt: one fact per file, update an existing file rather than duplicating it, add the `MEMORY.md` pointer line.

Output the inventory as a numbered checklist. Include the files you considered and ruled out, with the reason — that's what stops a stale doc from hiding behind "I assumed it was fine".

## Phase 3 — Apply the updates

For each candidate, in order:

1. **Read what you're about to edit.** Default mode: the budget rules above apply. `--end`: read the whole file.
2. **Cross-check its claims against Phase 1.** What does it assert that is no longer true? What new thing has no coverage at all?
3. **Apply precise edits.** Surgical, matching the file's existing style. Don't rewrite unless the file is fundamentally wrong.
4. **Mark the line**: `✓ <absolute path> — <one-line outcome>` or `✗ <absolute path> — not affected (<reason>)`.

Never "improve" a doc for something this session didn't change.

## Phase 4 — Write the state file

Rewrite `.claude/session-state.md` **in full**, every run. Never append — a stale line from two sessions ago is worse than no file.

Get the timestamp with `date '+%Y-%m-%d %H:%M'`.

In `--end` mode, the next reader is a brand-new session with no summary of this one. Write for a cold reader: no "as discussed", no pronoun whose antecedent lives in the conversation, "Key files" filled with care.

```markdown
# Session state — <project name>
_Written by /save-state on <YYYY-MM-DD HH:MM>. Regenerated in full at each run — don't hand-edit._

## Current task
<2-3 sentences: what is being worked on and why>

## Next step
<the single next concrete action — one sentence>

## Done this session
- <change> — `<absolute path>`

## Decisions + why
- <decision> — <the reason it beat the alternative>

## Traps
- <gotcha that would cost time to rediscover> — or "none"

## Key files
- `<absolute path>` — <why to read it first>

## Running state
- Background processes: <shell IDs + kill command> — or "none"
- Dev servers / ports: <url + port> — or "none"
- Branch: <name> — Uncommitted: <n files, or "clean">

## Open questions
- <question waiting on the user> — or "none"
```

In `--end` mode, a background process still running when the user closes the session dies with it, or keeps running orphaned. Name it under "Running state" with its kill command either way.

Then make sure the file stays out of git:

```bash
grep -q '^\.claude/session-state\.md$' .gitignore 2>/dev/null || echo '.claude/session-state.md' >> .gitignore
```

If `.gitignore` doesn't exist, create it with that one line.

## Phase 5 — Git

**Without `--commit`:** report, don't act. List the uncommitted files, group them by what they belong to, and propose a conventional commit message (or several, if the work splits cleanly). Do not stage, do not commit.

**With `--commit`:** apply the commit rules from `SKILL.md`, then report the resulting commit hash and subject line.

## Phase 6 — How the turn ends

End the turn in the language the user is working in.

### Default mode — the two blocks

**Block A — the compaction command.** `/compact` accepts free-form instructions; use them to steer the summary toward this specific task instead of a generic recap.

```
/compact Focus on: <current task>. Keep: the decisions and their reasons, the uncommitted files and their state, the traps (<name them>), the open questions. Drop: exploration that led nowhere, the full contents of files already edited, tool output already acted on.
```

**Block B — the prompt to send right after.** Short by design: the compacted session keeps its summary, so this only needs to re-anchor it.

```
<one line naming the task>. Read /<absolute path>/.claude/session-state.md first — it holds the exact state at the moment of compaction. Then: <next step>.
```

### `--end` — report, then one resume line

No `/compact` block: nothing is being compacted.

First, the report: every Phase 2 line with its ✓ or ✗ outcome, then the git outcome (commit hash and subject, or the uncommitted files and the proposed message).

Then, last, the line to paste into the next session:

```
<one line naming the project and the task>. Read /<absolute path>/.claude/session-state.md first — it holds where the last session stopped. Then: <next step>.
```

## Anti-patterns

- Turning `session-state.md` into a session narrative. It's state: current task, next step, decisions, traps. Not a story.
- Updating a doc "while you're in there" for something this session didn't change.
- Reading the whole repo to be safe — in default mode, at 300k tokens, that *is* the risk.
- Skipping the state file because the docs got updated. Docs don't hold the next step.
- Saving session narrative into Claude memory. Memory holds durable facts, not what happened today.
- Handing a `/compact` block to a `--end` run.
- Opening the last block with "Here's your prompt:" or any framing line.
