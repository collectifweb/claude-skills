# rename-sessions

Renames every Claude Code session in a workspace so the `/resume` list can be read at a glance: a status emoji, then three to six words.

The problem it solves is small and constant. Auto-generated session titles are long, English, and phrased alike — "Review Termageddon assistant security changes", "Review Axeptio API integration for security", "Review security vulnerabilities in dashboard changes". Three of those and the list stops carrying information. After a few months you scroll past fifty of them looking for the session where you fixed that one thing.

## What a renamed list looks like

```
✅ Refonte de l'éditeur de rapport
✅ Optimize web crawler
✅ Page de garde PDF + sommaire
⏳ Mode Axeptio (M3/M4 restants)
🔒 /security-review - API Axeptio
🔒 /security-review - SSRF url-guard
🔒 /security-review - étape Mode (2)
```

Four status emojis, no more — past that, the list stops reading at a glance and each symbol loses its meaning:

| | |
| --- | --- |
| ✅ | done, shipped |
| ⏳ | in progress, or to pick up later |
| ⭐ | worth a look, decision pending |
| 🔒 | security review |

A session that is nothing but a skill invocation leads with the skill name: `✅ /tidy - purge des secrets`.

## How it works

The displayed title comes from the **last** `type: "custom-title"` line in `~/.claude/projects/<encoded-workspace>/<session-id>.jsonl`. Renaming is therefore an append:

```json
{"type":"custom-title","customTitle":"✅ Fix erreur feuille de route","sessionId":"<uuid>"}
```

Nothing is overwritten, which is what makes this safe to run on a workspace you care about. A title you dislike is fixed by appending one more line. Later `ai-title` lines do not take over.

## What it does

1. **Inventories** every session file — current title, auto-generated title, first user message, message count, date.
2. **Spots the families** — automatic security reviews and skill invocations often make up half the list. It tells them apart by what each one actually covered, so you don't end up with twenty identical titles.
3. **Reads titles you wrote yourself** before proposing anything. Those reveal your real convention, which wins over the one shipped here. A title already in shape keeps its text — it only gains the emoji.
4. **Backs up** the current state before writing anything.
5. **Refuses to run partially** — a coverage check aborts if any session in the folder has no title planned, or if a planned title points at no session. Dry run first, apply second.
6. **Verifies** afterwards that every session carries its new title and that no file became unreadable.

## Usage

```
/rename-sessions              # current workspace
/rename-sessions ~/Apps/xyz   # another workspace
```

It reports what it renamed, and flags every deviation from the convention with its reason rather than deciding quietly on a title you wrote by hand.

## Naming as you go

The bulk pass should only ever happen once. To have new sessions born with a decent title, add this to your `~/.claude/CLAUDE.md`:

```markdown
## Session naming

Name my sessions myself, without being asked: a status emoji, then 3–6 words.
✅ done · ⏳ in progress · ⭐ worth a look · 🔒 security review.
A session that is only a skill invocation leads with /skill-name.

I cannot detect the end of a session, so name early and refine:
1. As soon as the subject is clear, set a ⏳ title. A session cut short then
   still carries a fair title, and the leftover ⏳ says something true.
2. Update at milestones — verified deploy, proven fix → ✅.

The displayed title is the LAST `type: "custom-title"` line of
~/.claude/projects/<encoded-workspace>/<session-id>.jsonl. Appending a line
renames; nothing is overwritten. The current session's uuid is the parent
folder of the scratchpad path. Never guess it from the most recently
modified .jsonl — several sessions often run in parallel.
```

That last warning matters more than it looks. Picking the newest file works right up until you have two sessions open, and then it renames the wrong one.

## What it can't do

**Bring a session back to ✅ after you walk away from it.** Nothing runs once the window closes, so a session you abandon mid-work stays ⏳ until you reopen it or run the skill again. That's the cost of not being able to see the end — and it's why the convention treats ⏳ as a truthful default rather than a failure state.

**Requires:** Claude Code

**Linux / macOS**

```bash
ln -s "$(pwd)/claude-skills/rename-sessions" ~/.claude/skills/rename-sessions
```

**Windows** (PowerShell, admin / Developer Mode)

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\rename-sessions" -Target "$PWD\claude-skills\rename-sessions"
```
