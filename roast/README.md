# roast

A Claude Code skill that convenes a five-persona council to tear an idea apart before you build it, then hands down a single verdict. Written in French, in Alexandre's voice: short, concrete, no hedging.

## The problem

Claude agrees with you by default. That is exactly the wrong instinct when you are about to sink weeks into an idea. `roast` flips it: five independent personas attack and defend the idea from every angle, and a Judge resolves the tension into one honest call plus the cheapest test to de-risk it.

## How it works

1. **The brief** — one tight round of questions (idea, buyer + price, your edge, constraints), then a single paragraph pasted into every council member so all five judge the same thing.
2. **The council** — five agents run in parallel, each locked in character, none allowed to soften:
   - **Le Contrarien** — assumes it fails, hunts the fatal flaws.
   - **L'Expansionniste** — fights for the 10x upside.
   - **Le Logicien** — first principles only, no web, does the logic hold.
   - **Le Chercheur** — web research, real competitors, market signals.
   - **Le Client** — role-plays the target buyer in first person.
3. **The verdict** — the Judge weighs everything (not an average), folds in the money read, and returns one call.

## Output format

```
## LE VERDICT : FONCE / REMANIE / ABANDONNE
Confiance : [faible / moyenne / élevée]

**La décision en une ligne :** …
**Pourquoi :** …
**Le plus gros risque :** …
**Le plus gros potentiel :** …
**Lecture financière :** …
**Le test le moins cher en 48 h :** …
**Si REMANIE :** …

Contrarien X/10 · Expansionniste X/10 · Logicien X/10 · Chercheur X/10 · Client X/10
```

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/roast" ~/.claude/skills/roast
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
/roast une appli de covoiturage pour PME
```

Or type `/roast` alone and answer the brief questions. Works on business ideas as well as project, product, or feature ideas.

Also triggers on: "roaste mon idée", "démolis cette idée", "stress-teste ça", "réunis le conseil", "un deuxième avis brutal avant de me lancer".

## License

MIT. See [LICENSE](LICENSE).
