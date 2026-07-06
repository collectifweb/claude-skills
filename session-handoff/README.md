# session-handoff

Closes a Claude Code session cleanly so nothing is lost when you `/compact` or `/clear`. It runs in two phases:

1. **Persist** — writes what happened this session into the project's living docs: checks off completed to-dos, updates `CLAUDE.md` and any documentation that drifted. Changes are proposed for your approval, then applied.
2. **Hand off** — produces a chat recap (decisions, shipped changes, key files, running state, verification, deferrals, open questions) so a fresh agent picks up by reading it alone.

The result: the repo's docs end up accurate, and the next context — whether it's a post-compaction continuation or a brand-new session — resumes without losing continuity.

It's a **manual** skill. You run it when it's useful; it never blocks or forces itself before a `/compact`.

## The problem it solves

Two failures happen at end of session:

- **The docs go stale.** To-do items got done, `CLAUDE.md` picked up a new invariant, a command changed — but none of it is written down. After a compaction or a `/clear`, that knowledge is gone.
- **The handoff is thin.** Asked to "wrap up", models summarize the last few turns and drop the load-bearing details: background shell IDs, dev-server ports, the plan file that drove the work, relative paths a fresh working directory can't resolve.

session-handoff fixes both: it persists session outcomes into the repo *and* produces a fixed-shape recap, every time.

## What it does

**Phase 1 — persist (proposed, then applied):**

- **To-do** — checks off items completed this session (TodoWrite state + `tasks/todo.md` if the project uses one), adds follow-ups that surfaced
- **CLAUDE.md** — updates it when the project context changed (a new invariant, stack detail, or load-bearing gotcha)
- **Docs** — fixes the specific claims in `README.md` / `docs/**` / changelog that *this session* made stale
- **Lessons** — records any correction you made, if the project keeps a `tasks/lessons.md`

It lists every intended edit as a numbered list, waits for your OK, then applies them together. Session-scoped by design — it updates only what this session changed. For a full doc-vs-code audit, it points you to [`/doc-sync`](../doc-sync/) instead of expanding scope.

**Phase 2 — the handoff recap** captures, in chat:

- **Where it started** — the original ask and the constraints that emerged
- **Decisions locked + what shipped** — with the absolute path of where each change lives
- **Docs updated this handoff** — what Phase 1 wrote
- **Key files for next session** — plan file first, then everything worth reading before acting
- **Running state** — background shell IDs + kill commands, dev servers/ports, open worktrees
- **Verification** — the commands that prove things still work
- **Deferred + open questions** — what got pushed, and what still needs your input
- **Pick up here** — the single most likely next action

## Guardrails

- **Durable state goes to files; the recap stays in chat.** Phase 1 writes to the repo's docs; Phase 2's narrative is a chat recap, not another file.
- **Nothing is written silently.** Doc edits are proposed as one list and applied only after you approve.
- **Session-scoped, not a filesystem audit.** It synthesizes *this* session — no `git log`, no broad globs to reconstruct what happened. It reads the specific files it's about to edit, nothing wider.
- **Never invents state.** Empty section → "none". No doc needs a change → it says so instead of manufacturing edits.
- **Absolute paths, no emojis, no retrospective** — the tone of an engineer handing off at end-of-shift.

## Optional: transcript backup on auto-compaction

The `references/` folder ships one **non-blocking** hook script, `pre-compact-backup.sh`. Wired into a `PreCompact` hook (matcher `auto`), it copies the raw transcript aside when Claude Code auto-compacts — a last safety net if you didn't run a manual handoff in time. It never blocks compaction, and it's entirely optional; the skill works fully without it. There is deliberately **no** guard that forces a handoff before `/compact`.

## Requirements

- Claude Code (git optional)

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/session-handoff" ~/.claude/skills/session-handoff
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\session-handoff" -Target "$PWD\claude-skills\session-handoff"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you'll just lose auto-sync on `git pull`).

## When to use it

- End of a substantial session, right before you `/clear`
- Whenever you're about to hand the work to a fresh agent
- Before a manual `/compact`, so the next context starts with accurate docs and real state

## License

MIT. See [LICENSE](./LICENSE).
