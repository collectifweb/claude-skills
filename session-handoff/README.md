# session-handoff

Produces a structured end-of-session summary so you can `/clear` and start a fresh agent without losing continuity — the next agent picks up by reading the handoff alone.

Designed as a **context-handoff artifact**, not a status report: the audience is the next instance of Claude, not a stakeholder. Terse, concrete, and always the same shape so nothing important slips through between sessions.

## The problem it solves

When asked to "wrap up" or "summarize before I clear", models tend to:

- Summarize only the last few turns and call it a handoff
- Drop the load-bearing details — background process IDs, dev server ports, the plan file that drove the work
- Use relative paths the next agent (with a different working directory) can't resolve
- Turn it into a retrospective ("what went well") instead of state the next agent can act on

session-handoff enforces a fixed template with a "never invent state, write `none` instead" rule, so the structure stays stable every single time.

## What it captures

- **Where it started** — the original ask and the constraints that emerged
- **Decisions locked + what shipped** — with the absolute path of where each change lives
- **Key files for next session** — plan file first, then everything worth reading before acting
- **Running state** — background shell IDs + kill commands, dev servers/ports, open worktrees
- **Verification** — the commands that prove things still work
- **Deferred + open questions** — what got pushed, and what still needs the user's input
- **Pick up here** — the single most likely next action

## Guardrails

- The narrative is **chat-only** — never written to a file, never touches memory
- Synthesis of *this* session, not a filesystem audit — no `git log`, no broad globs
- Absolute paths always, so a fresh working directory doesn't break the references
- No emojis, no hype, no retrospective — the tone of an engineer handing off at end-of-shift

## Optional: compaction guard

The `references/` folder ships two reference hook scripts you can wire into a `PreCompact` hook:

- `pre-compact-guard.sh` — blocks a manual `/compact` until a fresh handoff exists (writes a tiny `.claude/handoff/.state.json` marker with no summary content)
- `pre-compact-backup.sh` — a non-blocking safety net that backs up the raw transcript on auto-compaction

These are optional. The skill works fully without them; they just make it hard to `/compact` a session you forgot to hand off.

## Requirements

- Claude Code (git optional — only needed for the compaction-guard marker)

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
- Before a manual `/compact`, so the next context starts with real state

## License

MIT. See [LICENSE](./LICENSE).
