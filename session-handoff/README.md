# session-handoff

Ends a Claude Code session with one **paste-ready handoff message** — posted alone, as the last message of the turn. Copy it, open a fresh session, paste, and the work resumes exactly where it stopped.

That copy-paste is the whole workflow, and everything in the skill serves it:

- The message is the **last** thing in the turn — nothing after it, so `/copy` grabs it clean.
- The message is **alone** — no preamble, no commentary wrapped around it.
- The message is **self-contained** — it gets read in an empty session, with no access to the conversation it came from.

It's a **manual** skill. You run it when it's useful; it never blocks or forces itself before a `/compact`.

## The problem it solves

Asked to "wrap up", a model summarizes the last few turns and drops exactly what the next agent needs: background shell IDs, dev-server ports, the plan file that drove the work, absolute paths a fresh working directory can resolve. Then it wraps the summary in chatter, so what you paste carries half a conversation with it.

session-handoff fixes the shape: same sections every time, written for someone who wasn't there.

## What the message contains

- **Where it started** — the original ask and the constraints that emerged
- **Decisions locked + what shipped** — with the absolute path of where each change lives
- **Key files for next session** — plan file first, then everything worth reading before acting
- **Running state** — background shell IDs + kill commands, dev servers/ports, open worktrees
- **Verification** — the commands that prove things still work
- **Deferred + open questions** — what got pushed, and what still needs your input
- **Pick up here** — the single most likely next action

## Guardrails

- **The message stands alone and ends the turn.** No preamble, no sign-off, no follow-up question. Anything else Claude has to say goes in an earlier message.
- **Written for a cold reader.** No "as discussed above", no reference to the session it came from, no pronoun whose antecedent is missing.
- **Nothing is written to disk.** No summary file, no doc edits, no `CLAUDE.md` changes. You carry the handoff by copy-paste. Docs drifted? That's [`/doc-sync`](../doc-sync/)'s job — the skill points at it instead of expanding scope.
- **No filesystem audit.** It writes what it already knows about the session — no `git log`, no broad globs to reconstruct what happened.
- **Never invents state.** Empty section → "none", never omitted. The fixed shape is the point.
- **Absolute paths, no emojis, no retrospective** — the tone of an engineer handing off at end-of-shift.

## Optional: transcript backup on auto-compaction

The `references/` folder ships one **non-blocking** hook script, `pre-compact-backup.sh`. Wired into a `PreCompact` hook (matcher `auto`), it copies the raw transcript aside when Claude Code auto-compacts — a last safety net if you didn't run a manual handoff in time. It never blocks compaction, and it's entirely optional; the skill works fully without it. There is deliberately **no** guard that forces a handoff before `/compact`.

## Requirements

- Claude Code

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

- End of a substantial session, right before you `/clear` and start over
- Whenever you're handing the work to a fresh agent
- Before a manual `/compact`, so the densest statement of where things stand is the last thing in context

## License

MIT. See [LICENSE](./LICENSE).
