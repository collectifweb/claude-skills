# claude-skills

A collection of Claude Code skills for power users. Each skill is a self-contained folder you can install individually.

## Skills

### [session-review](./session-review/)

Uses Codex (OpenAI CLI) as an independent second pair of eyes to review a Claude Code working session before you commit. Codex reads the session transcript and the uncommitted git diff, produces a numbered report, and Claude triages each finding — accepting, rejecting, or pushing back with a final round of debate.

**Requires:** Claude Code, Codex CLI, git, Python 3

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/session-review" ~/.claude/skills/session-review
```

---

### [confront-codex](./confront-codex/)

Validates a technical plan by running an iterative debate between Claude and Codex before any implementation starts. Claude proposes, Codex critiques, Claude responds — until both converge or surface a real disagreement for you to resolve.

**Requires:** Claude Code, Codex CLI

```bash
ln -s "$(pwd)/claude-skills/confront-codex" ~/.claude/skills/confront-codex
```

---

### [timelog-synthesis](./timelog-synthesis/)

Generates a ready-to-paste time log for a client project day. Splits the day into blocks based on git commits and Claude Code session activity (90-minute gap = new block), formatted for Toggl or any time-tracking tool.

**Requires:** Claude Code, git

```bash
ln -s "$(pwd)/claude-skills/timelog-synthesis" ~/.claude/skills/timelog-synthesis
```

---

### [humanize](./humanize/)

Rewrites French text to remove LLM writing tics. Detects and corrects 36 categories of patterns (em-dashes, hollow intensifiers, dead verbs, Oxford comma, rule of three…) without touching the ideas or voice. Scores the text on a 0–100 slop scale and lists every correction made.

**Requires:** Claude Code

```bash
ln -s "$(pwd)/claude-skills/humanize" ~/.claude/skills/humanize
```

---

### [tidy](./tidy/)

Reorganizes documentation, archives obsolete plans, removes scratch files, and audits exposed secrets so Claude Code can navigate the project in a fresh session without getting lost. Produces a justified markdown report in `docs/tidy/`, then executes changes category by category with your approval at each step. `/tidy --deep` extends analysis to application code (orphan modules) — always proposed as questions, never auto-deleted.

**Requires:** Claude Code, git

```bash
ln -s "$(pwd)/claude-skills/tidy" ~/.claude/skills/tidy
```

---

## Install all at once

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
for skill in session-review confront-codex timelog-synthesis humanize tidy; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.claude/skills/$skill
done
```

Verify by opening a Claude Code session and typing `/help` — the skills should appear in the list.

## License

MIT. See each skill's folder for its own LICENSE file.
