# claude-skills

A collection of Claude Code skills for power users. Each skill is a self-contained folder you can install individually.

## Skills

### [session-review](./session-review/)

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

### [confront-codex](./confront-codex/)

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

### [timelog](./timelog/)

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

### [humanize](./humanize/)

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

### [tidy](./tidy/)

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

## Install all at once

**Linux / macOS**

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
for skill in session-review confront-codex timelog humanize tidy; do
  ln -s "$(pwd)/claude-skills/$skill" ~/.claude/skills/$skill
done
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
foreach ($skill in 'session-review','confront-codex','timelog','humanize','tidy') {
  New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\$skill" -Target "$PWD\claude-skills\$skill"
}
```

> **Note Windows** — Les liens symboliques exigent soit une session PowerShell *Administrateur*, soit l'activation du **Mode Développeur** (Paramètres → Confidentialité et sécurité → Pour les développeurs). À défaut, copiez les dossiers (`Copy-Item -Recurse`) au lieu de créer un symlink — vous perdrez juste la synchro automatique avec un `git pull`.

Verify by opening a Claude Code session and typing `/help` — the skills should appear in the list.

## License

MIT. See each skill's folder for its own LICENSE file.
