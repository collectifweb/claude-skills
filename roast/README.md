# roast

A Claude Code and Codex CLI skill that composes a jury of personas fit to whatever you are judging, runs them in parallel to tear it apart, then hands down a single verdict. Written in French, in Alexandre's voice: short, concrete, no hedging.

## The problem

The assistant agrees with you by default. That is exactly the wrong instinct when you are about to sink weeks into something — or when you need an honest read on something you already shipped. `roast` flips it: a jury of independent personas attacks and defends from every angle, and a Judge resolves the tension into one honest call plus the first thing to do to de-risk it.

A polite jury is useless. The whole value is friction. So the casting adapts to the subject, but three guarantees never move — otherwise it is not a roast:

1. **A front-line demolisher** — one persona whose only job is to break it.
2. **A real outside voice** — never an internal abstraction: the actual user, client, or market.
3. **A Judge who decides** — one call, not an average of scores.

## How it works

1. **Frame it** — identify the family (idea/offer · project in design · finished artifact · other), gather a tight brief, then **propose a named 5-persona casting** drawn from that family and let the user adjust it in one line. If the subject is visual (a site, a mockup), grab a URL or screenshot so the jury judges what it actually sees.
2. **Convene the jury** — all personas run in parallel from one shared brief, each locked in character. For a visual roast, each one opens the screenshot and judges the real rendering.
3. **The verdict** — the Judge weighs the tension (not an average), folds in the cost/impact read, and returns one call.

Example castings:

- **Idea / offer** — L'avocat du diable · Le visionnaire · Le cartésien · L'enquêteur (marché) · Le client.
- **Project in design** — Dev front · Dev back/intégration · Designer UX · Designer UI · L'utilisateur qui s'en servira.
- **Finished artifact** — Le visiteur pressé (mobile) · Le client potentiel sceptique · L'œil technique (perf/a11y/SEO) · L'utilisateur cible · Le proprio qui paie.

## Output format

```
## LE VERDICT : FONCE / AJUSTE / LAISSE TOMBER
Confiance : [faible / moyenne / élevée]

**La décision en une ligne :** …
**Pourquoi :** …
**Le plus gros risque :** …
**Le plus gros potentiel :** …
**Lecture coût / impact :** …
**Par où commencer :** …
**Si AJUSTE :** …

[Persona 1] X/10 · [Persona 2] X/10 · …
```

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/roast" ~/.claude/skills/roast
```

To also expose it to Codex CLI:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/claude-skills/roast" ~/.codex/skills/roast
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\roast" -Target "$PWD\claude-skills\roast"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you'll just lose auto-sync on `git pull`).

Verify by opening a Claude Code session — `roast` should appear in `/help`.

## Usage

```
/roast le design de la page d'accueil de monsite.ca
```

Or type `/roast` alone and answer the brief. Works on business ideas, on projects you are about to build, and on things that already exist (a live site, a mockup, a document).

Also triggers on: "roaste mon idée", "démolis ce site", "stress-teste ça", "réunis le jury", "un deuxième avis brutal avant de me lancer".

## License

MIT. See [LICENSE](LICENSE).
