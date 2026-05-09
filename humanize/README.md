# humanize

A Claude Code skill that rewrites French text to remove LLM writing tics and make it sound human. Detects and corrects 36 categories of patterns — from em-dashes to hollow intensifiers — without touching the ideas, arguments, or voice.

## Why

Text produced by an LLM has recognizable fingerprints: em-dashes everywhere, capital letters after colons, "massive" and "crucial" modifying everything, transitions that connect nothing. This skill runs a structured pass on any French text before it reaches a human reader.

## What it changes

Two absolute rules — zero tolerance:

- **Em-dash (—)** — the single most visible LLM marker in French. Replaced with a period, comma, colon, or parentheses depending on context.
- **Capital after colon** — incorrect in French. `Résultat : Les ventes` → `Résultat : les ventes`.

Then a full sweep across three levels:

| Level | Examples |
|---|---|
| Errors (always fixed) | Hollow intensifiers (massif, crucial, incontournable), dead verbs (permettre de, s'avérer, constituer), dead transitions (il convient de souligner, force est de constater), compulsive summary (en résumé, pour conclure) |
| Warnings (fixed when they accumulate) | Abstract nouns (paradigme, synergie, levier), Oxford comma, rule of three, systematic bold, systematic lists |
| Positive injections (added when missing) | Logical connectors, sentence length variation, register breaks, concrete anchors |

## Output format

```
**Score slop** : XX/100
(90-100 = propre, 70-89 = tics mineurs, 50-69 = patterns IA visibles, 0-49 = output IA brut)

**Ce qui a été corrigé** :
- [original → remplacement, par catégorie]

---

[Le texte réécrit — pas de préambule, juste le texte propre.]
```

## Installation

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/humanize" ~/.claude/skills/humanize
```

Verify by opening a Claude Code session — `humanize` should appear in `/help`.

## Usage

```
/humanize
```

Or paste text directly after the command. Works on the last Claude output if no argument is given.

Also triggers on: "humaniser ce texte", "virer le slop", "nettoyer le style IA", "ça sonne ChatGPT", "rendre ça naturel".

## Reference file

`references/tics-llm.json` contains all 36 rules with exhaustive word lists, before/after examples, thresholds, and exceptions. Claude reads it when a nuanced judgment call is needed.

## License

MIT. See [LICENSE](LICENSE).
