# claude-skills

A collection of Claude Code skills for power users. Each skill is a self-contained folder you can install individually.

## Skills at a glance

| Skill | In one sentence |
| --- | --- |
| [humanize](#humanize) | Rewrites French text to strip LLM writing tics, without touching the ideas or the voice. |
| [confront-codex](#confront-codex) | Runs an iterative debate between Claude and Codex on a technical plan until they converge — before a single line of code is written. |
| [timelog](#timelog) | Generates a paste-ready time log for a client project day, split by git commits and Claude/Codex sessions. `quick` variant: multi-day, multi-project overview with no hours. |
| [tidy](#tidy) | Reorganizes docs, archives stale plans, audits exposed secrets — so a fresh Claude session finds its bearings fast. |
| [doc-sync](#doc-sync) | Cross-checks every documentation claim against the actual code, file by file, with a final audit report. |
| [roast](#roast) | Convenes five contrarian personas to pressure-test an idea before you build it — verdict FONCE / REMANIE / ABANDONNE. |
| [session-handoff](#session-handoff) | Ends a session with one paste-ready handoff message — copy it into a fresh session and the work resumes where it stopped. |
| [save-state](#save-state) | Writes the session's truth to disk before a `/compact`, then hands you the `/compact` line and the prompt to send right after. |
| [rename-sessions](#rename-sessions) | Renames every session in a workspace to a status emoji plus three to six words, so the `/resume` list reads at a glance. |

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

A `quick` variant (`/timelog quick`, `/timelog quick 7`, `/timelog quick YYYY-MM-DD..YYYY-MM-DD`) scans all Claude Code and Codex CLI sessions on the machine and prints a per-day overview of which projects you touched — no hours, no blocks.

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

Ends a session with one fixed-shape **handoff message**, posted alone as the last message of the turn: decisions, shipped changes, key files, running state (background shell IDs, ports), verification, deferrals, open questions. Written for a cold reader — copy it, open a fresh session, paste, and the work resumes where it stopped. Nothing before it, nothing after it, so a copy grabs exactly what you need. It writes no files and edits no docs (that's `/doc-sync`'s job). Manual and non-blocking; ships one optional, non-blocking transcript-backup hook.

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

## save-state

Run before a manual `/compact`. Compaction is a lossy save: the session knows the current task, the reasons behind the last decisions, the half-finished file and the trap you hit an hour ago — the files know none of it. save-state lists what the session changed, updates only the docs and task files those changes made false, writes `.claude/session-state.md` (rewritten in full each run, gitignored), reports the uncommitted work, then ends with two blocks to paste: `/compact` carrying instructions written for your actual task, then the short prompt that re-anchors the compacted session. `--commit` also makes the commit; it never pushes. Scoped by design, because it runs when context is nearly full — for the exhaustive pass, use `/doc-sync`.

**Requires:** Claude Code (git optional)

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/save-state" ~/.claude/skills/save-state
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\save-state" -Target "$PWD\claude-skills\save-state"
```

---

## rename-sessions

Auto-generated session titles are long, English, and phrased alike — three "Review X for security vulnerabilities" in a row and the `/resume` list stops carrying information. This renames every session in a workspace to a status emoji plus three to six words (✅ done · ⏳ in progress · ⭐ worth a look · 🔒 security review), telling apart the families that dominate the list — automatic security reviews, skill invocations — by what each one actually covered. Titles you wrote by hand keep their text and only gain the emoji. Renaming is an append, so nothing is overwritten and a title you dislike is fixed with one more line; a coverage check aborts rather than renaming a workspace halfway. Ships the `CLAUDE.md` rule that names new sessions as they go, so the bulk pass only happens once.

**Requires:** Claude Code

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/rename-sessions" ~/.claude/skills/rename-sessions
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\rename-sessions" -Target "$PWD\claude-skills\rename-sessions"
```

---

## Install all at once

**Linux / macOS**

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
for skill in humanize confront-codex timelog tidy doc-sync roast session-handoff save-state rename-sessions; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.claude/skills/$skill
done
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
foreach ($skill in 'humanize','confront-codex','timelog','tidy','doc-sync','roast','session-handoff','save-state') {
  New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\$skill" -Target "$PWD\claude-skills\$skill"
}
```

> **Windows note** — Symbolic links require either an *Administrator* PowerShell session or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, copy the folders (`Copy-Item -Recurse`) instead of creating a symlink — you'll just lose the automatic sync on `git pull`.

Verify by opening a Claude Code session and typing `/help` — the skills should appear in the list.

## License

MIT. See each skill's folder for its own LICENSE file.
