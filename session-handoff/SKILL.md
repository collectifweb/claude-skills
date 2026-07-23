---
name: session-handoff
description: Use at end of session — when the user says "session handoff", "wrap up session", "hand off", "handoff summary", or is about to /clear and start over. Produces one paste-ready handoff message as the entire final message of the turn — decisions, shipped changes, key files, running state, verification, deferrals, open questions — written for a cold reader so it can be copied into a brand-new session and resume the work from nothing. It writes no files and edits no docs.
---

# Session Handoff

Produce a **paste-ready handoff message**: one block, posted as the entire final message of the turn, written so the user can copy it, open a fresh session, paste it, and have the work resume exactly where it stopped.

That copy-paste is the whole workflow. Everything in this skill serves it:

- The message is the **last** thing in the turn — nothing after it, so a copy grabs it clean.
- The message is **alone** in that turn — no preamble, no commentary wrapped around it.
- The message is **self-contained** — it will be read in an empty session with no access to this conversation.

This skill writes nothing to disk. It doesn't update docs, `CLAUDE.md`, or task files — if those drifted, that's `/doc-sync`'s job, or a dedicated doc skill. Say so in one line if you notice drift, then hand off anyway; don't expand scope.

It is a **manual** skill. Run it by hand when it's useful. It is never required before a `/compact`.

## When to invoke

User says: "session handoff", "wrap up session", "hand off", "handoff summary", "let's wrap up", "summarize before I clear", or any near-equivalent. Also invoke proactively if the user says they're about to `/clear` or start a fresh session without having run it yet — but never block them if they decline.

## What to pull from

Build the recap from what you already know about this session — not from a filesystem audit. No `git log`, no broad globs to reconstruct what happened. Sources:

- The original request and the constraints that emerged along the way.
- Decisions made and changes shipped, with the file each one lives in.
- Plan files referenced this session (check `~/.claude/plans/` if a plan was mentioned).
- TodoWrite state — what's done, what's still open.
- Background processes started with `run_in_background` — shell IDs are load-bearing.
- Files created or modified; memory files touched.
- Unresolved questions in either direction — yours to the user, and the user's to you.

## Output template — use exactly this structure, every time

```
# Session Handoff — <one-line title of what this session was about>

## Where it started
<2-3 sentences: what the user asked for, key framing or constraints that emerged>

## Decisions locked + what shipped
- <decision or change> — <why, and where it lives (absolute path if a file)>
- ...

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

1. **The message is the last message, and it stands alone.** No preamble ("here's your handoff"), no sign-off, no question after it. The final message is the template, and only the template. Anything you need to say to the user goes in an earlier message.
2. **Write it for a cold reader.** It gets pasted into an empty session: no "as discussed above", no reference to this chat, no pronoun whose antecedent lives outside the block. If it doesn't stand on its own, it fails.
3. **Nothing is written to disk.** No summary file, no doc updates, no `CLAUDE.md` edits. The user carries the handoff by copy-paste.
4. **Never invent state.** If a section has nothing to report, write "none" — do not omit the section. Structure stability is the whole point.
5. **Absolute paths always.** The next agent may have a different working directory.
6. **If a plan file drove the session, name it first** in "Key files" so the next agent reads it before anything else.
7. **No emojis, no hype, no "great job" summaries.** Terse and concrete — paths, commands, shell IDs, decisions. The tone of a seasoned engineer handing off at end-of-shift.
8. **Background process IDs are critical.** If you started any `run_in_background` shells, their IDs must appear in "Running state" with the kill command — the next agent cannot find them otherwise.

## Optional — transcript backup on auto-compaction

`references/pre-compact-backup.sh` is a **non-blocking** safety net you can wire into a `PreCompact` hook (matcher `auto`): it copies the raw transcript aside when Claude Code auto-compacts, in case a manual handoff wasn't run in time. It never blocks compaction. Wiring it is entirely optional and independent of this skill — the skill works fully without it. It is the only script this skill ships; there is deliberately no guard that forces a handoff before `/compact`.

## Anti-patterns — do not do these

- Adding anything after the handoff block: a comment, an offer to adjust it, a question. The block ends the turn.
- Opening the final message with "Here's the handoff:" or any other framing line.
- Summarizing the last 3 turns and calling it a handoff.
- Updating docs, `CLAUDE.md`, or task files from this skill. Not its job — point at `/doc-sync` and move on.
- Reconstructing the session with `git log` or broad globs instead of writing what you know.
- Listing files by relative path.
- Skipping the "Running state" section because "nothing is running" — write "none" instead.
- Adding a "what went well / what went poorly" retrospective. This isn't a retro.
- Recommending next steps beyond the single "Pick up here" line. The next agent decides; you just hand off.
