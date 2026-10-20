# claude-skills

A collection of skills for power users of **Claude Code** and **Codex CLI**. Each skill is a self-contained folder you can install individually. All of them run in Claude Code; all but `audit-secu` and `rename-sessions` also run in Codex CLI (same folder, linked into `~/.codex/skills`).

## Skills at a glance

| Skill | In one sentence | Codex CLI |
| --- | --- | --- |
| [humanize](#humanize) | Rewrites French text to strip LLM writing tics, without touching the ideas or the voice. | yes |
| [confront-codex](#confront-codex) | Runs an iterative debate on a technical plan between the agent you're in and a second, independent one (Codex from Claude, Claude from Codex, or Fable with `--fable`) until they converge — before a single line of code is written. | yes |
| [timelog](#timelog) | Generates a paste-ready time log for a client project day, split by git commits and Claude/Codex sessions. `quick` variant: multi-day, multi-project overview with no hours. | yes |
| [tidy](#tidy) | Reorganizes docs, archives stale plans, audits exposed secrets — so a fresh agent session finds its bearings fast. | yes |
| [doc-sync](#doc-sync) | Cross-checks every documentation claim against the actual code, file by file, with a final audit report. | yes |
| [roast](#roast) | Convenes five contrarian personas to pressure-test an idea before you build it — verdict FONCE / REMANIE / ABANDONNE. | yes |
| [save-state](#save-state) | Writes the session's truth to disk before a `/compact` (or at session end), then hands you the `/compact` line and the prompt to send right after. `--quick` and `--end` variants. | yes |
| [impression](#impression) | Prepares and checks print-ready files for board games, booklets, leaflets and posters: exact trim size, bleed, fonts, resolution, before/after contact sheets, questions for the printer. | yes |
| [audit-secu](#audit-secu) | Scans every project in a workspace for known vulnerable dependencies, GitHub Dependabot alerts, vulnerable WordPress plugins, end-of-life frameworks and outdated AI model IDs, then triages each finding with subagents and a Codex second opinion. Read-only. | no |
| [rename-sessions](#rename-sessions) | Renames every session in a workspace to a status emoji plus three to six words, so the `/resume` list reads at a glance. | no |

---

## humanize

Rewrites French text to remove LLM writing tics. Detects and corrects 44 categories of patterns (em-dashes, hollow intensifiers, dead verbs, Oxford comma, rule of three, AI chat residue, phantom authority, invisible watermark characters…) without touching the ideas or voice. Scores the text on a 0–100 slop scale and lists every correction made.

**Requires:** Claude Code or Codex CLI

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

Validates a technical plan by running an iterative debate before any implementation starts. The agent you're in proposes, a second, read-only agent critiques (Codex when run from Claude Code, Claude when run from Codex, Fable with `--fable`), and the debate goes on until both converge or surface a real disagreement for you to resolve. `--model` picks the Codex model, even from an approximate name.

**Requires:** Claude Code and Codex CLI (either one can host the debate)

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

Generates a ready-to-paste time log for a client project day. Splits the day into blocks based on git commits and Claude Code and Codex CLI session activity (15-minute gap = new block), formatted for Toggl or any time-tracking tool.

A `quick` variant (`/timelog quick`, `/timelog quick 7`, `/timelog quick YYYY-MM-DD..YYYY-MM-DD`) scans all Claude Code and Codex CLI sessions on the machine and prints a per-day overview of which projects you touched — no hours, no blocks.

**Requires:** Claude Code or Codex CLI, git, Python 3

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

Reorganizes documentation, archives obsolete plans, removes scratch files, and audits exposed secrets so a fresh Claude Code or Codex session can navigate the project without getting lost. Produces a justified markdown report in `docs/tidy/`, then executes changes category by category with your approval at each step. `/tidy --deep` extends analysis to application code (orphan modules) — always proposed as questions, never auto-deleted.

**Requires:** Claude Code or Codex CLI, git

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

Reconciles every documentation claim against the actual code instead of just summarizing the session. Builds a checklist of every doc file (README, CLAUDE.md, AGENTS.md, `docs/**`), reads each one in full, cross-checks every claim, and produces a final audit report — no silent skips. Built for end-of-session wrap-up so the next session starts on accurate docs.

**Requires:** Claude Code or Codex CLI

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

Composes a jury of personas fit to whatever you are judging, runs them in parallel to tear it apart, then a Judge returns one verdict (FONCE / AJUSTE / LAISSE TOMBER) with the first thing to do to de-risk it. The casting adapts to the subject — a business idea, a project you are about to build, or a finished artifact like a live site or mockup — but three guarantees never move: a front-line demolisher, a real outside voice, and a Judge who decides. For visual subjects the jury judges an actual screenshot, not a description. Written in French.

**Requires:** Claude Code or Codex CLI

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/roast" ~/.claude/skills/roast
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\roast" -Target "$PWD\claude-skills\roast"
```

---

## save-state

Run before a manual `/compact`. Compaction is a lossy save: the session knows the current task, the reasons behind the last decisions, the half-finished file and the trap you hit an hour ago — the files know none of it. save-state lists what the session changed, updates only the docs and task files those changes made false, writes `.claude/session-state.md` (rewritten in full each run, gitignored), reports the uncommitted work, then ends with two blocks to paste: `/compact` carrying instructions written for your actual task, then the short prompt that re-anchors the compacted session. `--quick` is for when auto-compaction is minutes away: the state file is written first and stale docs are listed for after the compaction instead of fixed. `--end` closes the session: every affected doc read in full, no `/compact` block, one line to paste into the next session. `--commit` combines with any mode and makes the commit; it never pushes. Scoped by design, because it runs when context is nearly full — for the exhaustive pass, use `/doc-sync`.

**Requires:** Claude Code or Codex CLI (git optional)

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/save-state" ~/.claude/skills/save-state
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\save-state" -Target "$PWD\claude-skills\save-state"
```

---

## impression

Prepares and checks files for a print shop: board games (board, cards, box), booklets, leaflets, posters. Sets the frame before designing (trim size, bleed, safe margin), prints an HTML page to PDF through Chrome at the exact size with TrimBox and BleedBox declared, checks a PDF (embedded fonts, image resolution, page boxes, text too close to the trim, words lost between two versions) and builds before/after contact sheets. Every print figure is tied to a cited source (PDF spec, ISO 15930, Ghent Workgroup, ICC) or flagged as something to confirm with the printer. Written in French; complements a visual design skill rather than replacing it.

**Requires:** Claude Code or Codex CLI, Python 3, poppler-utils, ImageMagick; pypdf and a Chrome for the HTML → PDF script

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/impression" ~/.claude/skills/impression
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\impression" -Target "$PWD\claude-skills\impression"
```

---

## audit-secu

Scans every project folder in a workspace (default `~/Apps-coding`, minus a trash folder) and reports what needs updating, without changing anything. A dependency-free Python script does the deterministic part in about a minute: `npm audit`, `pnpm audit`, `composer audit` (plus abandoned packages and major versions behind), pinned `requirements.txt` against OSV, WordPress core, plugins and themes by version against WPVulnerability (CC0 data), GitHub Dependabot, code scanning and secret scanning alerts, end-of-life dates from endoflife.date, and hard-coded AI model IDs checked against a model table. Lock files that belong to third-party WordPress plugins are skipped, along with the Dependabot alerts that point at them. The skill then has one subagent per affected project judge whether each vulnerability is reachable and in production code, sends severe or uncertain verdicts to Codex for a second opinion, and writes a single report ranked by urgency. Before each run, a private claude.ai page (the audit panel, `selection.html`) lets you switch projects in or out of the scan, with an optional reason; the script then honours the last selection. A switched-off project can still be watched: it is scanned without triage, and its high or critical findings are checked against the live site with anonymous public requests, then listed as possible offers for the client. Reports stay outside the repository. Written in French.

**Requires:** Claude Code, Python 3, npm, composer, `gh` (logged in) for GitHub alerts, Codex CLI for the second opinion; pnpm if a project uses it. The model table is read from the `maj-modeles` skill (`~/.claude/skills/maj-modeles/model-map.json`); without it, every model ID is reported as unknown.

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/audit-secu" ~/.claude/skills/audit-secu
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\audit-secu" -Target "$PWD\claude-skills\audit-secu"
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
for skill in humanize confront-codex timelog tidy doc-sync roast save-state impression audit-secu rename-sessions; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.claude/skills/$skill
done

# Codex CLI (every skill except audit-secu and rename-sessions)
mkdir -p ~/.codex/skills
for skill in humanize confront-codex timelog tidy doc-sync roast save-state impression; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.codex/skills/$skill
done
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
foreach ($skill in 'humanize','confront-codex','timelog','tidy','doc-sync','roast','save-state','impression','audit-secu','rename-sessions') {
  New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\$skill" -Target "$PWD\claude-skills\$skill"
}

# Codex CLI (every skill except audit-secu and rename-sessions)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
foreach ($skill in 'humanize','confront-codex','timelog','tidy','doc-sync','roast','save-state','impression') {
  New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.codex\skills\$skill" -Target "$PWD\claude-skills\$skill"
}
```

> **Windows note** — Symbolic links require either an *Administrator* PowerShell session or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, copy the folders (`Copy-Item -Recurse`) instead of creating a symlink — you'll just lose the automatic sync on `git pull`.

Verify by opening a Claude Code session and typing `/help` — the skills should appear in the list.

## License

MIT. See each skill's folder for its own LICENSE file.
