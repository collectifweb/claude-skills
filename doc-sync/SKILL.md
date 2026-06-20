---
name: doc-sync
description: Sync project docs (README.md, CLAUDE.md, docs/*.md) with actual code. Trigger /doc-sync, "update the docs", "sync documentation", "refresh docs", or end-of-session wrap-up.
---

# doc-sync

Sync project documentation to match the actual code. Designed for end-of-session use in Claude Code, when context is approaching its limit and the user wants to start fresh next time with documentation that is 100% accurate.

## The core problem this skill solves

When asked to "update the docs", models tend to:
- Update the obvious files (README, the most-visible doc) and skip the rest
- Update the parts of a file they happen to think of, leaving stale sentences a few paragraphs down
- Treat the task as "summarize the session" instead of "reconcile every doc claim against the current code"
- Stop early because the diff "looks updated enough"

This skill exists to make that impossible by enforcing a strict, auditable workflow with a written checklist that must be completed before the task is considered done.

**Read this entire SKILL.md before starting. Do not skim.**

## Required workflow

You MUST execute these phases in order. Do not collapse, skip, or reorder them. Output the phase headers as you go so the user can see your progress.

### Phase 1 — Inventory

Build a complete list of every documentation file in the project. Do not rely on memory of which files exist.

Run, from the project root:

```bash
ls -la README.md CLAUDE.md 2>/dev/null
find docs -type f -name "*.md" 2>/dev/null | sort
find . -maxdepth 2 -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null | sort
```

Then produce a numbered list of every doc file you found. This list is your checklist. Every file on it must be processed in Phase 3. No exceptions.

If you find doc files in unexpected locations (e.g. `architecture/`, `wiki/`, package-level READMEs in subdirectories), include them too. When in doubt, include.

### Phase 2 — Session change summary

Before touching any doc, write a structured summary of what actually changed in this session. Cover every category below — write "none" explicitly if a category has no changes, so it's clear you considered it rather than forgot it:

- **Architecture & structure**: new modules, deleted modules, refactors, file moves
- **Public API**: new/changed/removed functions, classes, endpoints, route signatures, props, types
- **Data model**: schema changes, new tables/collections, migrations, new fields
- **Dependencies**: added, removed, or version-bumped packages
- **Configuration**: new env vars, config file keys, feature flags
- **Commands & workflows**: new npm/cargo/make scripts, changed build/test/deploy steps
- **Behavior & UX**: user-visible behavior changes that docs might describe
- **Technical decisions**: notable choices made this session (e.g. "switched from X to Y because Z")

This summary is your reference for Phase 3. Every change listed here must be cross-checked against every doc file.

### Phase 3 — File-by-file reconciliation

For **each** file in your Phase 1 checklist, in order:

1. **Read the file in full.** Not partial reads. Not "I remember what's in it." Read it.
2. **Cross-reference every factual claim** in that file against:
   - Your Phase 2 summary (did this session contradict it?)
   - The actual current code (is the claim still true regardless of this session?)
3. **List, explicitly**, every line/section that needs updating, plus every section that should be added because new functionality has no doc coverage yet.
4. **Apply the edits.** Use precise edits, not full rewrites, unless the file is fundamentally outdated.
5. **Mark the checklist item done** by re-stating: `✓ <filepath> — <one-line summary of changes, or "no changes needed">`

Critically: a file getting `no changes needed` is a valid outcome, but you must have actually read it and reasoned about it to claim that. Do not skip files because you assume they're untouched.

### Phase 4 — Cross-doc consistency pass

Documentation often describes the same concept in multiple places (e.g. install steps in README and in `docs/getting-started.md`; an API in `docs/api.md` and CLAUDE.md's quick reference). After Phase 3, do one more pass:

- For each major concept touched in Phase 2, list every doc location that mentions it.
- Verify those locations now agree with each other. If two docs describe the same thing in incompatible ways, fix it.
- Verify terminology is consistent (same name for the same thing across files).

### Phase 5 — Final report

Output a final report with:

- The complete checklist from Phase 1, every item marked ✓ with its outcome
- A "changes by file" summary
- A "concepts cross-checked" list from Phase 4
- An honest **"not updated and why"** section for anything you deliberately left alone (e.g. "CHANGELOG.md — out of scope, user maintains manually")
- A **self-audit question**: "Is there any change from Phase 2 that I cannot point to a doc update for?" Answer it. If yes, go back and fix it before declaring done.

## Anti-laziness rules

These exist because the default failure mode of this task is shortcut-taking. Follow them strictly.

1. **Never claim to have updated a file you didn't actually edit or explicitly mark `no changes needed` after reading.** No silent skips.
2. **Never batch-summarize doc files as "looked fine".** Each file gets its own explicit checklist line.
3. **If you find yourself wanting to stop early because "the important stuff is done"**, that's the exact moment to keep going. The remaining files are where staleness hides.
4. **Read full files, not snippets.** A grep-and-patch approach misses context-dependent claims (e.g. a paragraph that's now contradicted by a later section).
5. **Don't trust your memory of doc contents from earlier in the session.** Re-read.
6. **CLAUDE.md gets the same scrutiny as everything else.** It's often the most outdated file because it's written for future sessions and easy to forget.
7. **If the project has a `docs/` subdirectory with many files, do not collapse them into one mental category.** Each is a distinct file requiring distinct review.

## When the user has a partial scope in mind

Sometimes the user will say "just update the API docs" or similar. In that case:
- Confirm the scope with them briefly, then run the same workflow restricted to the named files.
- Still do Phase 4 (cross-doc consistency) within the restricted scope.
- Note in the final report what was intentionally out of scope.

## Output style during the run

Keep narration tight. Use the phase headers as section markers. Show the checklist as it progresses. Don't editorialize about how thorough you're being — just be thorough.
