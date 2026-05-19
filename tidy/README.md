# tidy

Range et organise un projet pour que Claude Code (ou n'importe quel dev) retrouve tout instantanément en ouvrant une nouvelle session.

Après plusieurs itérations, un projet accumule : plans d'anciennes features à la racine, scripts one-off oubliés, docs éparpillées, snapshots de debug, configs obsolètes, parfois même des secrets accidentellement commités. Ce skill fait le tri.

## Ce qu'il fait

- **Analyse** la documentation et la structure du repo (sans toucher au code applicatif par défaut)
- **Classifie** chaque fichier : à garder, à déplacer, à archiver, à supprimer, ou ambigu
- **Audite** la sécurité : `.env` trackés, clés API hardcodées, secrets dans l'historique git
- **Produit** un rapport global dans `docs/tidy/report-AAAA-MM-JJ.md` justifié ligne par ligne
- **Exécute** avec approbation séquentielle par catégorie (déplacements → archivages → suppressions → sécurité → questions)
- **Met à jour** les références cassées dans les autres fichiers après chaque déplacement
- **Propose** un commit conventionnel sans le pousser

## Modes

### `/tidy` (par défaut)

Périmètre : docs (`*.md`, `*.txt`), scripts orphelins (`*.sh`, `*.py` à la racine), configs doublonnées, snapshots de debug. Le code applicatif (`src/`, `app/`, `lib/`, `tests/`) n'est **jamais** touché.

### `/tidy --deep`

Étend l'analyse au code applicatif : détecte les modules jamais importés, les exports orphelins, les fichiers de tests pour du code qui n'existe plus. **Aucune suppression auto-proposée pour le code** — tout passe en mode question avec preuves jointes.

## Workflow

1. **Inventaire** — cartographie complète du repo, lecture de `CLAUDE.md` / `README.md` / `AGENTS.md`, catalogue de tous les candidats, métadonnées git par fichier, carte des références
2. **Classification** — chaque candidat reçoit une étiquette parmi `KEEP / MOVE / ARCHIVE / DELETE / ASK` selon des heuristiques explicites (référence ailleurs, âge, signaux de contenu, doublons)
3. **Audit sécurité** — scan de patterns connus (AWS, Anthropic, OpenAI, GitHub, JWT, private keys, URLs avec credentials), vérification des `.env` trackés, audit `.gitignore`
4. **Rapport** — fichier markdown structuré dans `docs/tidy/report-AAAA-MM-JJ.md`
5. **Exécution séquentielle** — catégorie par catégorie avec approbation : `GO` / `EDIT` / `SKIP` / `STOP`
6. **Méta-mise à jour** — patch des références cassées, suggestion de mise à jour `CLAUDE.md`, commit proposé

## Conventions appliquées

| Nature du fichier | Cible |
|---|---|
| Architecture, décisions | `docs/architecture/` |
| Plans / specs en cours | `docs/plans/` |
| Plans terminés | `docs/archives/<topic>/` |
| Incidents / RCAs | `docs/archives/incidents/AAAA-MM-JJ-<slug>/` |
| Guides | `docs/guides/` |
| Scripts utilitaires | `scripts/` |
| Scripts one-off historiques | `scripts/archive/` |
| Rapports de ce skill | `docs/tidy/` |

Si le projet a déjà une convention différente mais cohérente (`documentation/` au lieu de `docs/`), le skill la respecte.

## Garde-fous

- Toujours `git mv` / `git rm` (préserve l'historique)
- Jamais de suppression sans approbation explicite
- Aucun fichier référencé dans `CLAUDE.md` / `README.md` / `AGENTS.md` n'est touché
- Jamais d'amend ni de force-push
- Pas d'auto-commit
- Audit sécurité **best-effort** — pour les projets sensibles, le rapport recommande `gitleaks` / `trufflehog` en complément

## Prérequis

- Claude Code
- Repo git
- Working tree de préférence clean au démarrage (sinon le skill propose de stash/commit d'abord)

## Installation

**Linux / macOS** (bash / zsh)

```bash
git clone https://github.com/collectifweb/claude-skills.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/claude-skills/tidy" ~/.claude/skills/tidy
```

Pour aussi l'exposer à Codex CLI :

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/claude-skills/tidy" ~/.codex/skills/tidy
```

**Windows** (PowerShell — run as Administrator, or enable Developer Mode)

```powershell
git clone https://github.com/collectifweb/claude-skills.git
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\tidy" -Target "$PWD\claude-skills\tidy"
```

Pour aussi l'exposer à Codex CLI :

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.codex\skills\tidy" -Target "$PWD\claude-skills\tidy"
```

> **Note Windows** — Les liens symboliques exigent PowerShell en Administrateur ou le **Mode Développeur** activé (Paramètres → Confidentialité et sécurité → Pour les développeurs). À défaut, remplacez `New-Item -ItemType SymbolicLink` par `Copy-Item -Recurse` (vous perdrez la synchro auto au `git pull`).

## Quand l'utiliser

- Fin d'itération importante, avant une release
- Avant de revenir sur un projet après quelques semaines/mois
- Avant onboarding d'un nouveau dev
- Quand tu sens que Claude « part dans tous les sens » et n'arrive plus à se situer

## Quand ne pas l'utiliser

- Working tree avec gros changements non commités (commit ou stash d'abord)
- Projet de moins de 30 jours d'activité (rien à ranger)
- Repo non git (les opérations nécessitent `git mv` / `git rm`)

## License

MIT. See [LICENSE](./LICENSE).
