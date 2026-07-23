# save-state

Run it right before a manual `/compact`. It moves everything that is true **only in the conversation** onto disk, then hands you two blocks to paste: the `/compact` command carrying instructions written for your actual task, and the prompt to send right after it.

The mental model: **compaction is a lossy save.** Right now the session knows the current task, why the last three decisions went the way they did, which file is half-finished, and the trap you hit forty minutes ago. The files know none of that. After compaction a summary survives and the rest doesn't. Anything you want on the other side has to be written down first.

## The problem it solves

You hit 300k tokens, you compact, and the next turn starts from files that describe a version of the project that stopped being true three hours ago. The README documents the old API. `tasks/todo.md` shows items you already shipped. Nothing anywhere says what you were about to do next.

save-state closes that gap in the one window where it can be closed: while the session still remembers.

## What it does

1. **Lists what the session actually changed** — code, public surface, data model, config, behavior, decisions with their reasons, traps discovered, task progress.
2. **Finds only the files those changes made false** — project docs (`README.md`, `CLAUDE.md`, `docs/*.md`), working files (`tasks/todo.md`, `tasks/lessons.md`, plan files), and Claude memory when a genuinely durable fact emerged. Files considered and ruled out are listed with the reason, so nothing hides behind "looked fine".
3. **Writes `.claude/session-state.md`** — the anchor file, rewritten in full every run, gitignored automatically. Current task, next step, decisions and why, traps, key files, running state (background shell IDs, ports, branch), open questions.
4. **Handles git** — lists the uncommitted work and proposes a commit message. With `--commit`, it makes the commit too. Never pushes.
5. **Ends with two paste-ready blocks** — `/compact <tailored instructions>`, then the short prompt that re-anchors the compacted session on the state file.

## What it can't do

It **can't trigger the compaction**. Slash commands are run by the Claude Code CLI, not by the model, and the `PreCompact` hook fires *during* a compaction rather than starting one. So the run ends by handing you the exact line to paste. Two paste operations, and you're back at work.

## Usage

```
/save-state             # full run; git is reported on, not touched
/save-state --commit    # same, plus the commit is actually created (never pushed)
```

Manual only. Nothing invokes it automatically, and it never blocks a `/compact`.

## Guardrails

- **Scoped, not exhaustive.** It runs when context is nearly full, so a full-repo inventory is exactly the wrong move. Locating files is cheap; reading them isn't. Want the exhaustive pass? That's [`/doc-sync`](../doc-sync/).
- **The state file is written every run**, even when no doc needed a change. The docs don't hold your next step.
- **Rewritten in full, never appended.** A stale line from two sessions ago is worse than no file.
- **Never invents state.** Empty section → "none", never omitted. The fixed shape is what makes it readable in five seconds.
- **Absolute paths** in the state file and in the resume prompt — the working directory after compaction isn't guaranteed.
- **No commit without `--commit`**, no push ever, no `.env` or credentials staged, no AI-attribution footer.
- **Nothing after the resume prompt** — no comment, no follow-up question. A copy grabs it clean.

## How it differs from the neighbours

| | writes to disk | output | target |
| --- | --- | --- | --- |
| **save-state** | yes | short prompt + `/compact` line | a `/compact` |
| [session-handoff](../session-handoff/) | no | long self-contained handoff | a `/clear` |
| [doc-sync](../doc-sync/) | yes (docs only) | audit report | doc accuracy, any time |

## Requirements

- Claude Code (git optional)

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/save-state" ~/.claude/skills/save-state
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\save-state" -Target "$PWD\claude-skills\save-state"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you'll just lose auto-sync on `git pull`).

## When to use it

- The context bar is getting full and you know a `/compact` is next
- You're stopping for the day mid-task and want tomorrow to start from disk, not from memory
- Right after a stretch of decisions you'd hate to re-argue

## License

MIT. See [LICENSE](./LICENSE).
