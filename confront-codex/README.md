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

- **Claude Code** and **Codex CLI** — install Codex from https://developers.openai.com/codex/cli (the VSCode extension alone is not enough)
- `timeout` (GNU coreutils; `gtimeout` on macOS via Homebrew)

The skill works from either side. Run from Claude Code, the second opinion is Codex; run from Codex CLI, the second opinion is Claude (`claude -p`). With `--fable`, it is Fable from either side. The second agent runs read-only and its final answer is saved as the round file, so it can never modify your project.

With Codex as the second opinion, the default model is `gpt-5.6-sol` with `model_reasoning_effort="xhigh"`. If that model is refused, it falls back to `gpt-5.6-terra`, then `gpt-5.6-luna` — never to a more expensive model on its own. An outdated Codex CLI refuses recent models, sometimes with a misleading message (0.148.0 said `gpt-6-sol` was "not supported when using Codex with a ChatGPT account"; 0.156.1 accepts it on the same account). The skill checks `codex --version` before falling back.

Add `--fable` (or say "avec Fable") to get the second opinion from Claude's Fable model instead, via `claude -p --model fable`, read-only as well.

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

To make it available in Codex CLI as well:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/claude-skills/confront-codex" ~/.codex/skills/confront-codex
```

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

## Choose the model

Pass `--model`, or name the model in your trigger. Approximate spellings are fine: the skill reads the list of models your Codex install knows (`~/.codex/models_cache.json`), picks the matching one and announces it, or asks when two models match.

| You say | Effect |
|---|---|
| `/confront-codex --model 5.6terra` | uses `gpt-5.6-terra` |
| "confront-codex en 5.6 sol" | uses `gpt-5.6-sol` |
| "confront-codex with luna" | asks: `gpt-6-luna` or `gpt-5.6-luna`? |
| "without xhigh" | drops `model_reasoning_effort=xhigh` |
| "with reasoning high" | uses `model_reasoning_effort=high` (faster) |

## Contributing

Issues and PRs welcome. Most useful contributions:

- Improvements to the Codex prompts in `references/codex-prompts.md` based on real debate transcripts
- New examples in `references/exemples.md`

## License

MIT. See [LICENSE](LICENSE).
