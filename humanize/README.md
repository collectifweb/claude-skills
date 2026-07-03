# humanize

A Claude Code skill that rewrites French text to remove LLM writing tics and make it sound human. Pass it any text before it reaches a reader — report, email, article, LinkedIn post — and get back a clean version with a slop score and a list of every fix made.

## The problem

LLM-generated French has recognizable fingerprints. Some are glaring, some are subtle, all of them add up:

> *Dans ce contexte fondamentalement transformateur, il convient de souligner que notre approche — innovante et holistique — permet de mettre en lumière les enjeux cruciaux qui façonnent le paysage actuel. Non seulement elle répond aux défis de notre époque, mais elle offre également des perspectives nouvelles, illustrant ainsi la vitalité de notre démarche.*

That's a 56-word sentence with zero content. `humanize` finds every pattern that caused it and fixes them.

## What it corrects

### Two absolute rules — zero tolerance

**Em-dash (—)** — the single most visible LLM marker in French. Replaced with a period, comma, colon, or parentheses. One em-dash costs −10 points. Zero tolerance.

**Capital letter after colon** — wrong in French. `Résultat : Les ventes` → `Résultat : les ventes`.

### Errors — always fixed

| Pattern | Examples |
|---|---|
| Hollow intensifiers | massif, crucial, fondamental, incontournable, révolutionnaire, fascinant, véritablement, absolument |
| Dead verbs | permettre de, s'avérer, constituer, mettre en lumière, jouer un rôle, s'inscrire dans |
| Dead transitions | il convient de souligner, force est de constater, dans ce contexte, il est important de noter que, cela étant dit |
| Exploration calques | plonger dans, naviguer dans, explorer ensemble, tisser des liens, une riche tapisserie |
| Trailing fake analysis | soulignant ainsi l'importance de, illustrant la pertinence de, reflétant les enjeux de |
| Hollow opening sentences | dans un contexte de, à l'heure où, dans un monde en profonde transformation |
| Compulsive summary | en résumé, pour conclure, en définitive, au final, on retiendra que |
| Present participle as main verb | « Utilisant cette approche, l'équipe a progressé » → two proper sentences |
| Dramatic fragment opener | « La raison ? », « Bonne nouvelle : », « Résultat final : », « Petite confession : » → absorbed into a real sentence |
| Title case | « Les Avantages Du Télétravail » → « Les avantages du télétravail » |
| Oxford comma | « les pommes, les poires, et les bananes » → no comma before *et* |
| Emojis in headings and lists | removed unless editorial intent is explicit |

### Warnings — fixed when they accumulate

| Pattern | Threshold |
|---|---|
| Abstract nouns (paradigme, synergie, levier, démarche, dispositif…) | flag each occurrence |
| Corporate adjectives (pertinent, optimal, robuste, innovant, holistique…) | flag each occurrence |
| Redundant pairs (crucial et essentiel, complet et exhaustif…) | keep one |
| Sycophantic framing (enjeu majeur pour l'avenir, profondément humaniste…) | flag, ask for evidence |
| Fake subjectivity (ce qui me frappe, ce qui est intéressant, ce que je retiens…) | rephrase directly without the pseudo-reaction |
| Systematic bold | max 3 per text |
| Systematic lists | max 2 per text |
| Rule of three | max 1 per text |
| Défis/Perspectives couplet | flag the boilerplate close |
| Artificial thèse/antithèse balance | flag, push for a real position |

### Positive injections — added when missing

| What | Target |
|---|---|
| Logical connectors (car, donc, or, pourtant, en revanche…) | ≥ 1 per 4 sentences |
| Sentence length variation | 60 % long (15+ words) / 40 % short (< 10 words) |
| Register breaks | ≥ 1 per 400 words |
| Concrete anchors (date, name, sourced number, situated anecdote) | ≥ 1 per 300-word section |

## Output format

```
**Score slop** : XX/100
(90-100 = écriture humaine propre · 70-89 = quelques tics mineurs · 50-69 = patterns IA visibles · 0-49 = output IA brut)

**Ce qui a été corrigé** :
- Tiret cadratin × 2 → virgule / point
- "fondamentalement crucial" → "décisif"
- Transition morte supprimée : "il convient de souligner que"
- …

---

[Texte réécrit. Pas de préambule.]
```

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/humanize" ~/.claude/skills/humanize
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\humanize" -Target "$PWD\claude-skills\humanize"
```

> **Windows note** — Symbolic links require PowerShell as Administrator or **Developer Mode** enabled (Settings → Privacy & Security → For developers). Otherwise, replace `New-Item -ItemType SymbolicLink` with `Copy-Item -Recurse` (you'll just lose auto-sync on `git pull`).

Verify by opening a Claude Code session — `humanize` should appear in `/help`.

## Usage

```
/humanize
```

Or paste text directly after the command. Works on the last Claude output if no argument is given.

Also triggers on: "humaniser ce texte", "virer le slop", "nettoyer le style IA", "ça sonne ChatGPT", "rendre ça naturel", "prépare ça pour l'envoyer".

## Reference

`references/tics-llm.json` — 36 rules with exhaustive word lists, before/after examples, thresholds, and exceptions. Claude reads it for nuanced judgment calls on longer texts.

## License

MIT. See [LICENSE](LICENSE).
