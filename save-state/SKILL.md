---
name: save-state
description: Use before a manual /compact or at the end of a session — "save-state", "sauvegarde l'état", "je vais compacter", "prépare la compaction", "je ferme la session", "before I compact". Writes the session's truth to disk (docs and task files this session made stale, a rewritten .claude/session-state.md). Default ends with two paste-ready blocks, the /compact line and the resume prompt. --quick is for when auto-compaction is imminent — state file first, docs deferred. --end closes the session — fuller doc pass, no compaction blocks, one resume line for the next session. --commit combines with any mode. Manual only; it cannot trigger /compact itself.
---

# save-state

**Compaction is a lossy save.** The session knows the current task, why the last decisions went the way they did, the half-finished file, the trap hit an hour ago. The files know none of it. Anything wanted on the other side has to be written down first. The same holds when the session simply ends.

## Modes

| Invocation | When | Docs | Ends with |
| --- | --- | --- | --- |
| `/save-state` | a `/compact` is coming | scoped to what the session changed | `/compact` block + resume prompt |
| `/save-state --quick` | auto-compaction is minutes away | **deferred**, listed in the state file | same two blocks, shorter |
| `/save-state --end` | the session is over | every affected doc read in full | report + one resume line |

- `--commit` combines with any mode: the commit is also created.
- `--quick` and `--end` are mutually exclusive. If both are passed, ask which one was meant and do nothing else.
- **Default and `--end`: read `references/workflow.md` in this skill's folder now, and follow it.** It holds the full procedure.
- **`--quick`: do not read anything else.** The procedure is below, complete.

This skill **cannot run `/compact`**: slash commands are executed by the Claude Code CLI, not by the model, and the `PreCompact` hook fires during a compaction without being able to start one. Never claim the compaction was triggered.

## Rules for every mode

1. **The state file `.claude/session-state.md` is written every run**, rewritten in full, never appended. It must stay out of git: `grep -q '^\.claude/session-state\.md$' .gitignore 2>/dev/null || echo '.claude/session-state.md' >> .gitignore`.
2. **Never invent state.** An empty section gets "none", never gets dropped.
3. **Absolute paths everywhere**, in the state file and in every block to paste.
4. **No commit without `--commit`.** With it: stage by explicit path (never `git add -A`), only files this session touched, never `.env`, credentials or keys, never unrelated pre-existing changes (leave them, mention them). Never push. No `Co-Authored-By`, no AI-attribution footer. Check with `git show --stat HEAD` and report hash + subject.
5. **The last block ends the turn.** Nothing after it, no framing line before it. A copy has to grab it clean.
6. No emojis, no retrospective. Terse, concrete, paths and commands.

## `--quick` — the complete procedure

Only a few thousand tokens are left. Every tool call counts, and auto-compaction may cut the run short, so **the state file goes first**: if anything is lost, it must not be that.

**No file reads, no search, no doc edits, no memory writes.** Everything comes from what the session already knows. Stale docs are named, not fixed: the compacted session will fix them with room to spare.

1. One command: `git status --short; git branch --show-current; date '+%Y-%m-%d %H:%M'`
2. Write `.claude/session-state.md`, short form:

   ```markdown
   # Session state — <project name>
   _Written by /save-state --quick on <YYYY-MM-DD HH:MM>. Regenerated in full at each run — don't hand-edit._

   ## Current task
   <1-2 sentences>

   ## Next step
   <one sentence>

   ## Decisions + why
   - <decision> — <reason> — or "none"

   ## Traps
   - <gotcha> — or "none"

   ## Docs to update
   - `<absolute path>` — <what the session made false in it> — or "none"

   ## Running state
   - Background processes: <shell IDs + kill command> — or "none"
   - Branch: <name> — Uncommitted: <files, or "clean">

   ## Open questions
   - <question> — or "none"
   ```

   "Docs to update" lists the docs you know describe what the session changed. Don't search for them. If a durable fact for Claude memory emerged, add it under "Decisions + why" so it survives.
3. One command: the `.gitignore` line from rule 1, plus the commit if `--commit` (rule 4).
4. End with the two blocks, in the user's language:

   **Block A**
   ```
   /compact Focus on: <current task>. Keep: decisions and reasons, uncommitted files, traps (<name them>), open questions. Drop: dead-end exploration, file contents already edited, tool output already used.
   ```

   **Block B** — last thing in the turn
   ```
   <task in one line>. Read /<absolute path>/.claude/session-state.md first. Update the docs under "Docs to update", then: <next step>.
   ```
   If "Docs to update" is "none", drop that sentence.
