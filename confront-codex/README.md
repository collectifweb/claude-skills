# confront-codex

A Claude Code skill that stress-tests a technical plan by running a structured debate between Claude and Codex (OpenAI CLI) — round by round, until both converge on a consensus.

Use it after you've drafted a plan in Claude Code but before you start implementing. Codex reads the plan independently, challenges it, Claude responds, and the cycle repeats until agreement is reached or you're asked to arbitrate. The output is a clean, standalone plan document ready to execute.

## Why

Plans made with Claude share Claude's blind spots. Bringing in a second model with no investment in the existing proposal surfaces different objections — missed edge cases, questionable architecture choices, unconsidered alternatives. The debate format forces both sides to justify their positions rather than politely agree.

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│ Round 1                                                     │
│   • Claude writes its plan → docs/archives/.../round-1-claude.md │
│   • Codex reads it, challenges it → round-1-codex.md        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Round N (repeat until consensus)                            │
│   • Claude replies to Codex's critique → round-N-claude.md  │
│   • Codex re-evaluates, updates its position → round-N-codex.md │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Final output                                                │
│   • Clean consolidated plan → docs/plan-{slug}.md           │
│   • Debate archive kept in docs/archives/ for traceability  │
└─────────────────────────────────────────────────────────────┘
```

Capped at 5 rounds. If consensus isn't reached, Claude surfaces the sticking points and asks you to arbitrate.

## Requirements

- **Claude Code** — this skill runs inside a Claude Code session
- **Codex CLI** — install from https://developers.openai.com/codex/cli (the VSCode extension alone is not enough)

The skill defaults to `gpt-5.5` with `model_reasoning_effort="xhigh"`. Mention a different model or reasoning level in your trigger if you want to override.

## Installation

### As a personal skill (available across all projects)

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/confront-codex" ~/.claude/skills/confront-codex
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\confront-codex" -Target "$PWD\claude-skills\confront-codex"
```

### As a project skill (committed with a specific project)

**Linux / macOS**

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/collectifweb/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/confront-codex .claude/skills/confront-codex
```

**Windows** (PowerShell)

```powershell
cd C:\path\to\your\project
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
git clone https://github.com/collectifweb/claude-skills.git "$env:TEMP\claude-skills"
Copy-Item -Recurse "$env:TEMP\claude-skills\confront-codex" ".claude\skills\confront-codex"
```

> **Windows note** — Symbolic links require an Administrator PowerShell session or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` — you'll just lose the automatic sync on `git pull`.

Verify by opening a Claude Code session and typing `/help` — `confront-codex` should appear in the list.

## Usage

Trigger after finishing a plan in Claude Code:

```
/confront-codex
```

Or in natural language:

- "Confront this plan with Codex"
- "Validate the plan with Codex before we start"
- "Get a second opinion from Codex on this approach"
- "Challenge this plan"

Claude will ask for a short slug to name the debate folder, then run the rounds autonomously — checking in with you between rounds if there's anything to arbitrate.

## Output structure

```
docs/
├── plan-{slug}.md                           # The final consensus plan
└── archives/
    └── confront-codex-{slug}-YYYY-MM-DD-HHMM/
        ├── round-1-claude.md
        ├── round-1-codex.md
        ├── round-2-claude.md
        ├── round-2-codex.md
        └── ...
```

The `docs/plan-{slug}.md` is the deliverable — self-contained, clean, ready to execute. The archive is the reasoning trail.

## Override the Codex model

Mention it in your trigger:

| You say | Effect |
|---|---|
| "confront-codex with gpt-5.4" | uses `gpt-5.4` instead of `gpt-5.5` |
| "without xhigh" | drops `model_reasoning_effort=xhigh` |
| "with reasoning high" | uses `model_reasoning_effort=high` (faster) |

## Companion skill

To review a session *after* implementation rather than validate a plan *before* it, see [session-review](https://github.com/collectifweb/claude-skills/tree/main/session-review).

## Contributing

Issues and PRs welcome. Most useful contributions:

- Improvements to the Codex prompts in `references/codex-prompts.md` based on real debate transcripts
- New examples in `references/exemples.md`

## License

MIT. See [LICENSE](LICENSE).
