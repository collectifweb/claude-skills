# doc-sync

Reconciles every documentation claim in a project against the actual code — instead of "summarizing the session" or patching only the obvious files.

Designed for end-of-session use in Claude Code: when context is approaching its limit and you want the next session to start with documentation that is 100% accurate. It enforces a strict, auditable workflow so the usual shortcuts (update the README, forget the rest) become impossible.

## The problem it solves

When asked to "update the docs", models tend to:

- Update the most-visible file (README) and skip the others
- Fix the parts they happen to think of, leaving stale sentences a few paragraphs down
- Treat the task as "summarize what we did" instead of "verify every doc claim against the current code"
- Stop early because the diff "looks updated enough"

doc-sync makes that impossible with a written checklist that must be completed before the task counts as done.

## Workflow

1. **Inventory** — list *every* doc file in the project (`README.md`, `CLAUDE.md`, `docs/**/*.md`, package-level READMEs, `architecture/`, `wiki/`…). This list becomes the checklist; every file on it must be processed.
2. **Session change summary** — a structured rundown of what actually changed, by category (architecture, public API, data model, dependencies, config, commands, behavior, technical decisions). Each category is answered explicitly, "none" included.
3. **File-by-file reconciliation** — each file is read in full, every factual claim cross-checked against the change summary *and* the current code, then edited. Each file ends with `✓ <path> — <outcome>`. `no changes needed` is valid only after the file was actually read.
4. **Cross-doc consistency pass** — concepts described in multiple places (install steps, an API in `docs/api.md` and in `CLAUDE.md`) are verified to agree, with consistent terminology.
5. **Final report** — the full checklist with outcomes, a "changes by file" summary, concepts cross-checked, an honest "not updated and why" section, and a self-audit: *is there any change I can't point to a doc update for?*

## Guardrails

- No silent skips — every file is either edited or explicitly marked `no changes needed` after a real read
- Full-file reads, not grep-and-patch (context-dependent claims hide between paragraphs)
- `CLAUDE.md` gets the same scrutiny as everything else — it's usually the most outdated
- Honors a partial scope ("just the API docs") while still running the consistency pass within it

## Requirements

- Claude Code

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/doc-sync" ~/.claude/skills/doc-sync
```

To also expose it to Codex CLI:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/claude-skills/doc-sync" ~/.codex/skills/doc-sync
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\doc-sync" -Target "$PWD\claude-skills\doc-sync"
```

> **Note Windows** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & security → For developers). Otherwise replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you just lose auto-sync on `git pull`).

## When to use it

- End of a substantial session, before closing context
- Right before a release or handoff
- Whenever you suspect the docs have drifted from the code

## License

MIT. See [LICENSE](./LICENSE).
