---
name: save-state
description: Use right before a manual /compact — when the user says "save-state", "sauvegarde l'état", "je vais compacter", "prépare la compaction", "before I compact", "save the state". Writes the session's truth to disk while it still exists — updates the docs and task files this session made stale, rewrites .claude/session-state.md — then ends with two paste-ready blocks: the /compact line carrying custom instructions, and the prompt to send right after it. The --commit variant also commits the work. Manual only; it cannot trigger /compact itself.
---

# save-state

Run this when a `/compact` is coming. Its job is to move everything that is true **only in the conversation** onto disk, before compaction throws the conversation away.

That's the whole mental model: **compaction is a lossy save.** Right now the session knows the current task, why the last three decisions went the way they did, which file is half-finished, and the trap discovered forty minutes ago. The files know none of it. After compaction, a summary survives and the rest doesn't. Anything you want on the other side has to be written down first.

Two things come out of a run:

1. **Files on disk** — docs, task files, a `.claude/session-state.md` anchor, memory if warranted.
2. **Two paste-ready blocks** — the `/compact` command with instructions tailored to the current task, then the prompt to send immediately after it.

## What this skill cannot do

**It cannot run `/compact`.** Slash commands are executed by the Claude Code CLI, not by the model — there is no tool for it. The `PreCompact` hook fires *during* a compaction; it can't start one. So the run ends by handing the user the exact line to paste. Never claim otherwise, never pretend the compaction was triggered.

## Invocation

- `/save-state` — full run, git left alone (Phase 5 proposes a commit, doesn't make it).
- `/save-state --commit` — same run, plus the commit is actually created. Never pushed.

Manual only. Nothing invokes this automatically, and it never blocks a `/compact`.

## Related skills — don't do their job

- [`/doc-sync`](../doc-sync/) — exhaustive doc reconciliation, every file read in full. save-state is deliberately **scoped to what this session changed**, because it runs when context is nearly full and a full inventory is the opposite of what's needed. If the user wants exhaustive, point at `/doc-sync`.
- [`/session-handoff`](../session-handoff/) — for `/clear`, not `/compact`. Writes nothing to disk and produces a long self-contained handoff for an empty session. save-state writes to disk and produces a short prompt, because a compacted session keeps its summary.

## Context budget — this skill runs at 300k tokens

Every rule below exists because the run happens when context is nearly exhausted. Burning 30k tokens to prepare a compaction defeats the purpose.

- **No full-repo exploration.** No `git log`, no broad globs, no reading files you have no intention of editing.
- **Locating is cheap, reading is not.** `ls`, `find docs -name '*.md'`, and targeted `grep` for a stale claim are fine. Reading a 600-line doc to confirm it's unaffected is not.
- **A file you already read in full this session counts as read** — don't read it again unless something changed it since.
- **On a long file you're editing, re-read the section, not the file.**

## Required workflow

Execute in order. Output the phase headers so the user can follow. Keep narration tight.

### Phase 1 — What this session actually changed

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

### Phase 2 — Targeted inventory

For each of the four buckets, list the candidate files with a one-line reason. Candidates only — a file is a candidate when Phase 1 plausibly contradicts it, or when it describes the area the session touched.

**Bucket 1 — Project docs.** `README.md`, `CLAUDE.md`, `docs/*.md`, package-level READMEs. Locate them cheaply:

```bash
ls README.md CLAUDE.md 2>/dev/null
find docs -type f -name "*.md" 2>/dev/null | sort
```

Then filter against Phase 1. `CLAUDE.md` deserves a second look — it's written for future sessions, which is exactly what's about to happen.

**Bucket 2 — Working files.** `tasks/todo.md` (check off what shipped, add what emerged), `tasks/lessons.md` (any correction the user made this session), plan files referenced during the session (check `~/.claude/plans/` if a plan drove the work).

**Bucket 3 — The state file.** `.claude/session-state.md`. Always a target, every run, no exceptions. Phase 4 handles it.

**Bucket 4 — Claude memory.** `~/.claude/projects/<project-slug>/memory/`. Only if a **durable** fact emerged — a user preference, a constraint, an external reference that will still matter in three weeks. Not session narrative, not anything the repo already records. Follow the memory rules in the system prompt: one fact per file, update an existing file rather than duplicating it, add the `MEMORY.md` pointer line.

Output the inventory as a numbered checklist. Include the files you considered and ruled out, with the reason — that's what stops a stale doc from hiding behind "I assumed it was fine".

### Phase 3 — Apply the updates

For each candidate, in order:

1. **Read what you're about to edit** (see the budget rules above — a full read this session already counts).
2. **Cross-check its claims against Phase 1.** What does it assert that is no longer true? What new thing has no coverage at all?
3. **Apply precise edits.** Surgical, matching the file's existing style. Don't rewrite unless the file is fundamentally wrong.
4. **Mark the line**: `✓ <absolute path> — <one-line outcome>` or `✗ <absolute path> — not affected (<reason>)`.

Never "improve" a doc for something this session didn't change. Out of scope, out of budget.

### Phase 4 — Write the state file

Rewrite `.claude/session-state.md` **in full**, every run. Never append — a stale line from two sessions ago is worse than no file.

Get the timestamp with `date '+%Y-%m-%d %H:%M'`.

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

Then make sure the file stays out of git:

```bash
grep -q '^\.claude/session-state\.md$' .gitignore 2>/dev/null || echo '.claude/session-state.md' >> .gitignore
```

If `.gitignore` doesn't exist, create it with that one line.

### Phase 5 — Git

**Default (`/save-state`):** report, don't act. List the uncommitted files, group them by what they belong to, and propose a conventional commit message (or several, if the work splits cleanly). Do not stage, do not commit.

**With `--commit`:** stage the files that belong to this session's work and create the commit with that message. Then:

- **Never push.**
- **Never commit** `.env`, credentials, keys, or anything matching a secret pattern — exclude them and say so.
- **Never commit** unrelated pre-existing changes you didn't touch. Leave them, mention them.
- **No `Co-Authored-By`, no AI-attribution footer.**

Report the resulting commit hash and subject line.

### Phase 6 — The two blocks

End the turn with exactly two blocks, in this order, in the language the user is working in.

**Block A — the compaction command.** `/compact` accepts free-form instructions; use them to steer the summary toward this specific task instead of a generic recap.

```
/compact Focus on: <current task>. Keep: the decisions and their reasons, the uncommitted files and their state, the traps (<name them>), the open questions. Drop: exploration that led nowhere, the full contents of files already edited, tool output already acted on.
```

**Block B — the prompt to send right after.** Short by design: the compacted session keeps its summary, so this only needs to re-anchor it.

```
<one line naming the task>. Read /<absolute path>/.claude/session-state.md first — it holds the exact state at the moment of compaction. Then: <next step>.
```

Block B is the **last thing in the turn**. Nothing after it — no comment, no offer to adjust, no question. A copy has to grab it clean.

## Hard rules

1. **Never claim you triggered the compaction.** You handed over a line to paste. That's the whole extent of it.
2. **The state file is written every run**, even when nothing else needed updating. It's the anchor; the docs aren't.
3. **Never invent state.** An empty section gets "none", never gets dropped. The fixed shape is what makes the file readable in five seconds.
4. **Absolute paths everywhere** — in the state file and in Block B. The working directory after compaction is not guaranteed.
5. **No commit without `--commit`.** Ever.
6. **Scoped, not exhaustive.** If you catch yourself building a full doc inventory, stop — that's `/doc-sync`, and you don't have the context budget.
7. **No emojis, no retrospective, no "great session" wrap-up.** Terse, concrete, paths and commands.

## Anti-patterns

- Turning `session-state.md` into a session narrative. It's state: current task, next step, decisions, traps. Not a story.
- Appending to the state file instead of rewriting it.
- Updating a doc "while you're in there" for something this session didn't change.
- Reading the whole repo to be safe — at 300k tokens, that *is* the risk.
- Skipping the state file because the docs got updated. Docs don't hold the next step.
- Saving session narrative into Claude memory. Memory holds durable facts, not what happened today.
- Putting anything after Block B.
- Opening Block B with "Here's your prompt:" or any framing line.
