# timelog

A skill for **Claude Code and Codex CLI** that generates ready-to-paste time log entries for a client project, from git commit history and AI-assistant session activity (both Claude Code *and* Codex sessions are merged into the same timeline).

Run it at the end of the day (or later) from inside a client project repo. It reconstructs the day's work into time blocks — splitting on gaps longer than 90 minutes — and formats the output in a compact, Toggl-ready style.

## Why

Logging time accurately at the end of a long day is tedious and error-prone. This skill does the reconstruction automatically from three authoritative sources: your git commits (reliable timestamps, scoped to what actually changed), your Claude Code session transcripts and your Codex CLI session transcripts (both capture what you *asked* for, which often beats commit messages for intent).

If you use both Claude Code and Codex throughout the day, the skill fuses both transcript streams into one timeline so a block that spans both agents is logged as a single coherent task.

## How it works

1. Fetches all git commits for the target date authored by the current git user
2. Finds Claude Code session files for this project directory (in `~/.claude/projects/<encoded-path>/`)
3. Finds Codex CLI session files for the target date (in `~/.codex/sessions/YYYY/MM/DD/`) and filters them by `cwd` matching the current project
4. Extracts user message timestamps and content from all session JSONL files (Claude + Codex), filtering out system/AGENTS injected messages on the Codex side
5. Merges all events into a timeline and splits into blocks at 90-minute gaps
6. Summarizes each block in the user's style — direct, French, no em dashes, client-readable

Output is printed directly in the chat, ready to copy-paste into Toggl. No files created.

## Requirements

- **Claude Code** *or* **Codex CLI** — this skill runs inside either agent
- **git** — the project must be a git repository
- **jq** or **Python 3** — for parsing session JSONL files (usually pre-installed)

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

## Output format

```
9h-11h30 : task 1 - task 2 - task 3

14h-16h45 : task 4 - task 5
```

One block per line, blocks separated by a blank line. No markdown, no bullets, no em dashes. Style matches how a freelance dev would write their own time log.

## Notes

- Must be run from the root of a client project (git repo). The current directory determines which project's activity is analyzed.
- Codex sessions are stored by date (not by project), so filtering happens via the `cwd` field in each session's `session_meta` event. Only sessions launched from the current project directory (or a subdirectory) are counted.
- If nothing was committed and no Claude Code / Codex session exists for the project on the target date, the skill says so plainly rather than inventing activity.
- The skill writes its output to the chat only — it never creates or modifies project files.

## License

MIT. See [LICENSE](LICENSE).
