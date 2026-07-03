# claude-skills

A collection of Claude Code skills for power users. Each skill is a self-contained folder you can install individually.

## Skills at a glance

| Skill | In one sentence |
| --- | --- |
| [humanize](#humanize) | Rewrites French text to strip LLM writing tics, without touching the ideas or the voice. |
| [confront-codex](#confront-codex) | Runs an iterative debate between Claude and Codex on a technical plan until they converge — before a single line of code is written. |
| [timelog](#timelog) | Generates a paste-ready time log for a client project day, split by git commits and Claude/Codex sessions. |
| [tidy](#tidy) | Reorganizes docs, archives stale plans, audits exposed secrets — so a fresh Claude session finds its bearings fast. |
| [doc-sync](#doc-sync) | Cross-checks every documentation claim against the actual code, file by file, with a final audit report. |
| [roast](#roast) | Convenes five contrarian personas to pressure-test an idea before you build it — verdict FONCE / REMANIE / ABANDONNE. |
| [session-handoff](#session-handoff) | Produces a structured end-of-session summary so you can start on a fresh agent without losing continuity. |
| [session-review](#session-review) | Has Codex read the current Claude session (transcript + git diff) as an independent second pair of eyes before you commit. |

---

## humanize

Rewrites French text to remove LLM writing tics. Detects and corrects 36 categories of patterns (em-dashes, hollow intensifiers, dead verbs, Oxford comma, rule of three…) without touching the ideas or voice. Scores the text on a 0–100 slop scale and lists every correction made.

**Requires:** Claude Code

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/humanize" ~/.claude/skills/humanize
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\humanize" -Target "$PWD\claude-skills\humanize"
```

---

## confront-codex

Validates a technical plan by running an iterative debate between Claude and Codex before any implementation starts. Claude proposes, Codex critiques, Claude responds — until both converge or surface a real disagreement for you to resolve.

**Requires:** Claude Code, Codex CLI

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/confront-codex" ~/.claude/skills/confront-codex
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\confront-codex" -Target "$PWD\claude-skills\confront-codex"
```

---

## timelog

Generates a ready-to-paste time log for a client project day. Splits the day into blocks based on git commits and Claude Code session activity (90-minute gap = new block), formatted for Toggl or any time-tracking tool.

**Requires:** Claude Code, git

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/timelog" ~/.claude/skills/timelog
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\timelog" -Target "$PWD\claude-skills\timelog"
```

---

## tidy

Reorganizes documentation, archives obsolete plans, removes scratch files, and audits exposed secrets so Claude Code can navigate the project in a fresh session without getting lost. Produces a justified markdown report in `docs/tidy/`, then executes changes category by category with your approval at each step. `/tidy --deep` extends analysis to application code (orphan modules) — always proposed as questions, never auto-deleted.

**Requires:** Claude Code, git

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/tidy" ~/.claude/skills/tidy
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\tidy" -Target "$PWD\claude-skills\tidy"
```

---

## doc-sync

Reconciles every documentation claim against the actual code instead of just summarizing the session. Builds a checklist of every doc file (README, CLAUDE.md, `docs/**`), reads each one in full, cross-checks every claim, and produces a final audit report — no silent skips. Built for end-of-session wrap-up so the next session starts on accurate docs.

**Requires:** Claude Code

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/doc-sync" ~/.claude/skills/doc-sync
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\doc-sync" -Target "$PWD\claude-skills\doc-sync"
```

---

## roast

Convenes a five-persona council to pressure-test an idea before you build it. Five agents run in parallel — Contrarian, Expansionist, Logician, Researcher, Buyer — each locked in character and forbidden to hedge, then a Judge weighs the tension and returns one verdict (FONCE / REMANIE / ABANDONNE) with the cheapest 48-hour test to de-risk the riskiest assumption. Written in French. Works on business ideas and on product, project, or feature calls.

**Requires:** Claude Code (the Researcher persona uses web search)

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/roast" ~/.claude/skills/roast
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\roast" -Target "$PWD\claude-skills\roast"
```

---

## session-handoff

Produces a structured end-of-session summary so you can `/clear` and start a fresh agent without losing continuity. A fixed template captures decisions, shipped changes, key files, running state (background shell IDs, ports), verification steps, deferrals, and open questions — chat-only, terse, and the same shape every time. Ships optional `PreCompact` hook scripts that block a manual `/compact` until a fresh handoff exists.

**Requires:** Claude Code (git optional)

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/session-handoff" ~/.claude/skills/session-handoff
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\session-handoff" -Target "$PWD\claude-skills\session-handoff"
```

---

## session-review

Uses Codex (OpenAI CLI) as an independent second pair of eyes to review a Claude Code working session before you commit. Codex reads the session transcript and the uncommitted git diff, produces a numbered report, and Claude triages each finding — accepting, rejecting, or pushing back with a final round of debate.

**Requires:** Claude Code, Codex CLI, git, Python 3

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/session-review" ~/.claude/skills/session-review
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\session-review" -Target "$PWD\claude-skills\session-review"
```

---

## Install all at once

**Linux / macOS**

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
for skill in humanize confront-codex timelog tidy doc-sync roast session-handoff session-review; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.claude/skills/$skill
done
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
foreach ($skill in 'humanize','confront-codex','timelog','tidy','doc-sync','roast','session-handoff','session-review') {
  New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\$skill" -Target "$PWD\claude-skills\$skill"
}
```

> **Windows note** — Symbolic links require either an *Administrator* PowerShell session or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, copy the folders (`Copy-Item -Recurse`) instead of creating a symlink — you'll just lose the automatic sync on `git pull`.

Verify by opening a Claude Code session and typing `/help` — the skills should appear in the list.

## License

MIT. See each skill's folder for its own LICENSE file.
