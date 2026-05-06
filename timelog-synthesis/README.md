# timelog-synthesis

A Claude Code skill that generates ready-to-paste time log entries for a client project, from git commit history and Claude Code session activity.

Run it at the end of the day (or later) from inside a client project repo. It reconstructs the day's work into time blocks — splitting on gaps longer than 90 minutes — and formats the output in a compact, Toggl-ready style.

## Why

Logging time accurately at the end of a long day is tedious and error-prone. This skill does the reconstruction automatically from two authoritative sources: your git commits (reliable timestamps, scoped to what actually changed) and your Claude Code session transcripts (what you *asked* for, which often captures intent better than commit messages).

## How it works

1. Fetches all git commits for the target date authored by the current git user
2. Finds Claude Code session files for this project directory
3. Extracts user message timestamps and content from the session JSONL files
4. Merges all events into a timeline and splits into blocks at 90-minute gaps
5. Summarizes each block in the user's style — direct, French, no em dashes, client-readable

Output is printed directly in the chat, ready to copy-paste into Toggl. No files created.

## Requirements

- **Claude Code** — this skill runs inside a Claude Code session
- **git** — the project must be a git repository
- **jq** or **Python 3** — for parsing session JSONL files (usually pre-installed)

## Installation

### As a personal skill (available across all projects)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/timelog-synthesis" ~/.claude/skills/timelog-synthesis
```

### As a project skill (committed with a specific project)

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/collectifweb/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/timelog-synthesis .claude/skills/timelog-synthesis
```

Verify by opening a Claude Code session and typing `/help` — `timelog-synthesis` should appear in the list.

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
- If nothing was committed and no Claude Code session exists for the project on the target date, the skill says so plainly rather than inventing activity.
- The skill writes its output to the chat only — it never creates or modifies project files.

## License

MIT. See [LICENSE](LICENSE).
