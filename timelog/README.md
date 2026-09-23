# timelog

A skill for **Claude Code and Codex CLI** that generates ready-to-paste time log entries for a client project, from git commit history and AI-assistant session activity (both Claude Code *and* Codex sessions are merged into the same timeline).

Run it at the end of the day (or later) from inside a client project repo. It reconstructs the day's work into time blocks — splitting on gaps longer than 90 minutes — and formats the output in a compact, Toggl-ready style.

## Why

Logging time accurately at the end of a long day is tedious and error-prone. This skill does the reconstruction automatically from three authoritative sources: your git commits (reliable timestamps, scoped to what actually changed), your Claude Code session transcripts and your Codex CLI session transcripts (both capture what you *asked* for, which often beats commit messages for intent).

If you use both Claude Code and Codex throughout the day, the skill fuses both transcript streams into one timeline so a block that spans both agents is logged as a single coherent task.

## How it works

The mechanical part is done by a bundled, read-only script, `scripts/timelog.py`, so it behaves the same in both agents:

1. Fetches the target date's git commits (all branches) authored by the current git user, with the files each one touched
2. Finds the Claude Code (`~/.claude/projects/`) and Codex CLI (`~/.codex/sessions/`) sessions whose recorded working directory is the current project or one of its subfolders
3. Filters on the timestamps inside each session, not on file dates, so a session resumed the next day counts for the right day
4. Keeps only what you actually typed or pasted (plus slash commands), dropping tool output, notifications and injected instructions
5. Converts everything to the machine's local time, merges it into one timeline and splits it into blocks at 90-minute gaps, with durations and a day total

The agent then summarizes each block in the user's style — direct, French, no em dashes, client-readable. AI help is written as "avec assistance d'IA", never by tool name.

Output is printed directly in the chat, ready to copy-paste into Toggl. No files created.

## Requirements

- **Claude Code** *or* **Codex CLI** — this skill runs inside either agent
- **git** — the project must be a git repository
- **Python 3** — runs the bundled script, standard library only (tested with 3.12)

## Installation

### As a personal skill (available across all projects, both agents)

Clone the monorepo and symlink the skill into each agent's skills directory.

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
# Claude Code
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/timelog" ~/.claude/skills/timelog
# Codex CLI
mkdir -p ~/.codex/skills
ln -s "$(pwd)/claude-skills/timelog" ~/.codex/skills/timelog
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
# Claude Code
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\timelog" -Target "$PWD\claude-skills\timelog"
# Codex CLI
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.codex\skills\timelog" -Target "$PWD\claude-skills\timelog"
```

After installing into Codex, restart the Codex CLI so it picks up the new skill.

### As a project skill (committed with a specific project)

**Linux / macOS**

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/collectifweb/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/timelog .claude/skills/timelog
```

**Windows** (PowerShell)

```powershell
cd C:\path\to\your\project
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
git clone https://github.com/collectifweb/claude-skills.git "$env:TEMP\claude-skills"
Copy-Item -Recurse "$env:TEMP\claude-skills\timelog" ".claude\skills\timelog"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you'll just lose auto-sync on `git pull`).

Verify by opening a Claude Code session and typing `/help` — `timelog` should appear in the list. On Codex, the skill is discovered automatically from `~/.codex/skills/` and surfaced in the AGENTS.md skill index at session start.

## Usage

Trigger from inside a client project directory:

```
/timelog
```

Or in natural language:

- "Generate today's time log"
- "What did I work on today?"
- "Summarize yesterday's session for Toggl"
- "Time log for 2026-05-05"

The skill defaults to today. Specify a date or "yesterday" if needed.

### Quick mode — multi-day project overview

For a fast "which projects did I touch recently" answer — no hours, no time blocks, no commits, just a per-day list of project names:

```
/timelog quick             # today only
/timelog quick 7           # last 7 days
/timelog quick 2026-07-15..2026-07-22
```

Unlike the default mode, quick mode does **not** need to be run from inside a project — it scans every Claude Code project directory (`~/.claude/projects/*`) and every Codex CLI session (`~/.codex/sessions/YYYY/MM/DD/*`) on the machine, groups by day, and prints project basenames.

```
15 juil : boutique-fleurs.ca, ma-boutique-stripe
16 juil : ma-boutique-stripe
18 juil : claude-skills, ma-boutique-stripe
```

## Output format

```
9h-11h30 (2h30) : task 1 - task 2 - task 3

14h-16h45 (2h45) : task 4 - task 5

Total journée : 5h15
```

One block per line, blocks separated by a blank line. No markdown, no bullets, no em dashes. Style matches how a freelance dev would write their own time log.

## Notes

- Must be run from the root of a client project (git repo). The current directory determines which project's activity is analyzed.
- If nothing was committed and no Claude Code / Codex session exists for the project on the target date, the skill says so plainly rather than inventing activity.
- The skill writes its output to the chat only — it never creates or modifies project files.

## License

MIT. See [LICENSE](LICENSE).
