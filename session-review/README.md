# session-review

A Claude Code skill that uses Codex (OpenAI CLI) as an independent second pair of eyes to review what just happened in a Claude Code working session.

At the end of a session — before you commit or close the terminal — `session-review` packages up the conversation and the uncommitted git diff, hands it to Codex for a critical review, then has Claude triage Codex's findings point by point. Optionally, Claude can push back on points it disagrees with and get Codex's final reply.

You walk away with an actionable checklist of what to address before merging.

## Why

Long Claude Code sessions tend to drift. Edge cases get postponed, tests get skipped "for now", documentation falls behind, security concerns get noted but not addressed. By the time you're ready to commit, you've lost track of what was deferred.

Asking Claude itself to self-review has limits — it shares the same blind spots that produced the gaps. A different model with no investment in the existing solution catches more.

This skill formalizes that handoff so it's a single command, not an ad-hoc dance with two CLIs.

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1 — Claude packages context                           │
│   • Extracts session transcript from ~/.claude/projects/    │
│   • Captures uncommitted git diff                           │
│   • Writes 01-context.md with honest self-assessment        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2 — Codex reviews                                     │
│   • Reads the context, explores the repo                    │
│   • Identifies missed edge cases, tests, security, perf,    │
│     docs, conventions                                        │
│   • Writes 02-codex-report.md with numbered recommendations │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3 — Claude triages                                    │
│   • For each recommendation: Accepted / Rejected /          │
│     Nuanced / To object                                     │
│   • Writes 03-claude-decisions.md with justifications       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4 (optional) — Claude objects, Codex replies          │
│   • Triggered automatically if Claude has objections        │
│   • Single round, no back-and-forth                         │
│   • Claude integrates Codex's replies into final decisions  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5 — Synthesis for the user                            │
│   • Critical / Important / Nice-to-have action items        │
│   • Each item points to a specific file:line                │
│   • Written to synthesis.md                                 │
└─────────────────────────────────────────────────────────────┘
```

All artifacts are stored in `docs/reviews/session-review-{slug}-{timestamp}/` so you can audit the reasoning trail later.

## Requirements

- **Claude Code** — this skill runs inside a Claude Code session
- **Codex CLI** — install from https://developers.openai.com/codex/cli (the VSCode extension alone is not enough)
- A **git repository** — the skill relies on `git diff` to scope what changed
- **Python 3** — used to extract the session transcript from the JSONL file

The skill defaults to invoking Codex with `gpt-5.5` and `model_reasoning_effort="xhigh"`. You can override either in your initial request to Claude (e.g., "run a session review with reasoning high" or "use gpt-5.4").

## Installation

### As a personal skill (available across all projects)

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

### As a project skill (committed with a specific project)

**Linux / macOS**

```bash
cd /path/to/your/project
mkdir -p .claude/skills
git clone https://github.com/collectifweb/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/session-review .claude/skills/session-review
```

**Windows** (PowerShell)

```powershell
cd C:\path\to\your\project
New-Item -ItemType Directory -Force -Path ".claude\skills" | Out-Null
git clone https://github.com/collectifweb/claude-skills.git "$env:TEMP\claude-skills"
Copy-Item -Recurse "$env:TEMP\claude-skills\session-review" ".claude\skills\session-review"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` — you'll just lose auto-sync on `git pull`.

Verify the skill is loaded by starting a Claude Code session and typing `/help` — `session-review` should appear in the available skills list.

## Usage

Trigger the skill at the end of a working session, before committing:

```
/session-review
```

Or in natural language:

- "Have Codex review what we just did"
- "Double-check this session with Codex"
- "Make sure we didn't miss anything"
- "Run a session review"

Claude will:

1. Ask you for a short slug (e.g., `auth-oauth-fix`) to name the review folder
2. Extract the session and git diff into `docs/reviews/session-review-{slug}-{timestamp}/`
3. Invoke Codex (this can take 5–15 minutes with `xhigh` reasoning effort — that's normal)
4. Triage Codex's recommendations, optionally push back on some
5. Hand you `synthesis.md` with concrete actions to take before commit

## Output structure

```
docs/reviews/
└── session-review-auth-oauth-fix-2026-05-06-1430/
    ├── 01-context.md            # What Claude packaged for Codex
    ├── 02-codex-report.md       # Codex's recommendations (numbered R1, R2, …)
    ├── 03-claude-decisions.md   # Claude's triage with justifications
    ├── 04-claude-objections.md  # (optional) Claude's pushback on specific points
    ├── 05-codex-replies.md      # (optional) Codex's final replies
    └── synthesis.md             # The actionable checklist for you
```

The `docs/reviews/` folder is intentionally part of the project tree — it's audit trail material that's worth keeping in version control. Add it to `.gitignore` if you'd rather not track it.

## Configuration

The skill reads a few things from the environment but doesn't require any setup:

- `cwd` determines which project's session is reviewed
- The current Claude Code session is identified by finding the most recently modified `.jsonl` in `~/.claude/projects/<encoded-cwd>/`
- Codex inherits whatever auth/config it's already set up with (ChatGPT login or API key)

If you have multiple Claude Code sessions running simultaneously in the same project, the skill will warn you and ask which one to review.

## Override the Codex model

Mention it in your initial request:

| You say | Effect |
|---|---|
| "run a session review with gpt-5.4" | uses `gpt-5.4` instead of `gpt-5.5` |
| "session review without xhigh" | drops `model_reasoning_effort=xhigh`, uses Codex default |
| "session review with reasoning high" | uses `model_reasoning_effort=high` (faster) |
| "fast session review" | combines `high` reasoning with no streaming for minimum latency |

## Limitations and notes

- **Single round of objections.** Claude pushes back at most once. If a real disagreement remains after Codex's reply, Claude resolves it alone in the synthesis. This is by design — endless debate isn't worth the tokens.
- **Token cost.** A typical review on a moderately busy session burns 50k–200k Codex tokens depending on repo size and reasoning level. The skill warns you if it detects a very large session.
- **Session detection heuristic.** Without a `$CLAUDE_SESSION_ID` env var (not yet exposed by Claude Code), the skill picks the most recently modified `.jsonl` as "the current session". Reliable in single-session usage, fragile under parallel sessions in the same repo.
- **Not a replacement for code review by humans.** Use this to catch what was missed during a session, not to skip the human review step on important changes.

## Companion skill

If you want a similar handoff to Codex but **before** implementation (validating a plan rather than reviewing finished work), see [confront-codex](https://github.com/collectifweb/claude-skills/tree/main/confront-codex) — it runs an iterative debate between Claude and Codex on a technical plan until consensus.

## Contributing

Issues and PRs welcome. The most useful contributions:

- Better session extraction (the current Python script is opinionated about what to keep)
- Improvements to the Codex prompts in `references/codex-prompts.md` based on what you observe in real reviews
- Translations of the skill itself (currently French)

## License

MIT. See [LICENSE](LICENSE).
