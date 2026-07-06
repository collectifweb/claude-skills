---
name: session-handoff
description: Use at end of session — when the user says "session handoff", "wrap up session", "hand off", "handoff summary", or is about to /clear or /compact. First persists what happened into the project's living docs (checks off completed to-dos, updates CLAUDE.md and any docs that drifted this session — proposed for approval, then applied), then produces a chat handoff covering decisions, shipped changes, key files, running state, verification, deferrals, and open questions. Leaves the repo accurate so a fresh agent — or a post-compaction context — resumes without losing continuity.
---

# Session Handoff

Close a session cleanly so nothing is lost when the context is compacted or cleared. This runs in two phases:

1. **Persist** — write what happened this session into the project's durable files (to-do list, CLAUDE.md, docs). The next context reads accurate files, not a stale summary.
2. **Hand off** — produce a chat recap so a fresh agent can pick up by reading it alone.

Serves both cases equally: after `/compact` the durable state lives in the repo; after `/clear` the recap plus the updated docs carry the continuity.

This is a **manual** skill. Run it by hand when it's useful. It is never required before a `/compact` — some sessions don't need it.

## When to invoke

User says: "session handoff", "wrap up session", "hand off", "handoff summary", "let's wrap up", "summarize before I clear/compact", or any near-equivalent. Also invoke proactively if the user says they're about to `/clear` or `/compact` without having run it yet — but never block them if they decline.

## Phase 1 — Persist session outcomes into the project

Goal: leave the repo's living documents reflecting what actually happened, so the state survives compaction.

1. **Build the session inventory from memory — not from a filesystem audit.** You know what happened this session; don't reconstruct it with `git log` or broad globs. Capture:
   - To-do / task items **completed** this session (from TodoWrite state and from any `tasks/todo.md` the project uses).
   - New tasks or follow-ups that surfaced.
   - Decisions made and changes shipped (with the file they live in).
   - Anything that changes what a doc **currently claims** — a new command, a renamed thing, a changed data model, a new invariant or gotcha.
   - Corrections the user made to you (for a lessons file, if the project keeps one).
2. **Map the inventory to concrete doc targets.** Only the files that genuinely need a change — typically some of:
   - `tasks/todo.md` (or wherever the project tracks tasks) — check off completed items, add new ones.
   - `CLAUDE.md` — update if the project context changed (stack detail, invariant, load-bearing gotcha).
   - `README.md`, `docs/**`, changelog — fix the specific claims this session made stale.
   - `tasks/lessons.md` — record any correction, if the project uses one.
   - **Read each target file before proposing an edit** — you need its current wording to change it precisely. Reading the files you're about to edit is fine; a broad audit to re-discover the session is not.
3. **Propose before applying.** Present a single numbered list of the edits you intend to make — one line per file: `<path> — <what changes and why>`. Then wait for the user's OK. Apply them together after approval. If the user trims the list, apply only what they kept.
4. **Session-scoped, not a full audit.** Update only what *this session* changed. Do not reconcile the entire doc set against the entire codebase — that is what `/doc-sync` is for. If the docs look broadly drifted beyond this session's work, say so and suggest `/doc-sync`; don't silently expand scope.
5. **"Nothing to persist" is a valid outcome.** If no doc needs a change, say so explicitly and move to Phase 2 — don't invent edits to look busy.

## Phase 2 — Produce the handoff recap (in chat)

Synthesis of what happened this session, for the next instance of you. The audience is a future agent, not a stakeholder.

- Pull state from: the Phase 1 inventory, plan files referenced this session (check `~/.claude/plans/` if a plan was mentioned), TodoWrite state, background processes you started with `run_in_background` (shell IDs are load-bearing), files you created or modified, memory files touched, and unresolved questions in either direction.
- Post the recap in chat using the template below. The recap itself is chat-only — the durable state already lives in the files you updated in Phase 1.

## Output template — use exactly this structure, every time

```
# Session Handoff — <one-line title of what this session was about>

## Where it started
<2-3 sentences: what the user asked for, key framing or constraints that emerged>

## Decisions locked + what shipped
- <decision or change> — <why, and where it lives (absolute path if a file)>
- ...

## Docs updated this handoff
- `<absolute path>` — <what was written (completed to-dos, CLAUDE.md invariant, doc claim fixed)>
- ... — or "none"

## Key files for next session
- `<absolute path>` — <why the next agent should read this first>
- Plan file: `<path>` (if a plan drove the session)
- Memory files touched: `<paths>` (if any)

## Running state
- Background processes: <shell IDs + what they are + how to kill> — or "none"
- Dev servers / ports: <url + port> — or "none"
- Open worktrees / branches: <paths> — or "none"

## Verification — how to confirm things still work
- `<command>` — <expected outcome>
- ...

## Deferred + open questions
- Deferred: <item> — <why pushed to later>
- Open: <question needing the user's input> — <context>

## Pick up here
<1-2 sentences: the single most likely next action for a fresh agent>
```

## Hard rules

1. **Persist durable state to files; keep the recap in chat.** Phase 1 writes to the project's docs/to-do/CLAUDE.md. Phase 2's narrative stays in chat — it doesn't get written to a summary file.
2. **Propose doc edits, apply on the user's OK.** Never edit CLAUDE.md, docs, or task files silently. One numbered list, one approval, then apply.
3. **Never invent state.** If a section of the recap has nothing to report, write "none" — do not omit the section. Structure stability is the whole point. Same for Phase 1: no doc needs changing → say so.
4. **Session-scoped.** Document only what this session changed. A full doc-vs-code audit is `/doc-sync`'s job — point to it rather than expanding scope.
5. **Absolute paths always.** The next agent may have a different working directory.
6. **If a plan file drove the session, name it first** in "Key files" so the next agent reads it before anything else.
7. **No emojis, no hype, no "great job" summaries.** Terse and concrete — paths, commands, shell IDs, decisions. The tone of a seasoned engineer handing off at end-of-shift.
8. **Background process IDs are critical.** If you started any `run_in_background` shells, their IDs must appear in "Running state" with the kill command — the next agent cannot find them otherwise.

## Optional — transcript backup on auto-compaction

`references/pre-compact-backup.sh` is a **non-blocking** safety net you can wire into a `PreCompact` hook (matcher `auto`): it copies the raw transcript aside when Claude Code auto-compacts, in case a manual handoff wasn't run in time. It never blocks compaction. Wiring it is entirely optional and independent of this skill — the skill works fully without it. It is the only script this skill ships; there is deliberately no guard that forces a handoff before `/compact`.

## Anti-patterns — do not do these

- Summarizing the last 3 turns and calling it a handoff.
- Skipping Phase 1 and only producing the chat recap — the point is that the repo's docs end up accurate, not just the chat.
- Editing CLAUDE.md or docs without proposing the changes first.
- Turning Phase 1 into a full doc audit — that's `/doc-sync`. Stay scoped to this session.
- Listing files by relative path.
- Skipping the "Running state" section because "nothing is running" — write "none" instead.
- Adding a "what went well / what went poorly" retrospective. This isn't a retro.
- Recommending next steps beyond the single "Pick up here" line. The next agent decides; you just hand off.
