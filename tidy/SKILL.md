---
name: tidy
description: Range documentation, archives et fichiers d'un projet, audite les secrets exposés. Trigger /tidy, "ranger le projet", "nettoyer la doc", "organiser les fichiers", "faire le ménage du repo", "housekeeping". Mode `--deep` analyse aussi le code (dead code).
---

# Tidy

Ce skill remet de l'ordre dans un projet qui s'est alourdi au fil des sessions : documentation éparpillée, plans d'anciennes features qui traînent à la racine, scripts one-off oubliés, configs obsolètes, secrets accidentellement commités. Il produit un **rapport global structuré** puis exécute les changements par catégorie avec ton approbation à chaque étape.

L'objectif : qu'une nouvelle session Claude Code (ou un nouveau dev) puisse ouvrir le projet et **comprendre instantanément** où est quoi, quel est l'état d'avancement, et ce qui est encore d'actualité.

## Quand l'utiliser

- Fin d'itération importante ou avant une release
- Avant de revenir sur un projet après plusieurs semaines/mois
- Avant onboarding d'un dev ou d'un freelance
- Quand l'utilisateur exprime que le projet "devient bordélique", "j'ai du mal à m'y retrouver", "Claude part dans tous les sens"
- Slash command `/tidy` ou `/tidy --deep`

**Ne pas utiliser** si :
- Le repo a des changements non commités importants (proposer de commit d'abord)
- Le repo n'est pas un dépôt git (la majorité des opérations utilisent `git mv` / `git rm`)
- Le projet a moins de 30 jours d'activité (probablement trop tôt pour avoir besoin de ménage)

## Modes

### Mode par défaut

Périmètre : tous les fichiers **hors code applicatif**.

Inclut :
- Documentation : `*.md`, `*.txt`, `NOTES*`, `PLAN*`, `CHANGELOG*`, `TODO*`, contenu de `docs/`, `doc/`, `documentation/`
- Scripts one-off à la racine ou dans `scripts/` : `*.sh`, `*.py`, `*.mjs`, `*.ts` utilitaires
- Configs orphelines : anciennes versions de `.eslintrc*`, `jest.config.*`, `vite.config.*` doublonnés
- Snapshots de debug : `dump-*`, `log-*`, `test-output-*`, `screenshot-*`, `*.bak`, `*.old`
- Anciens prompts / specs : `prompt-*`, `spec-*`, `agent-*`

Exclut (jamais touché en mode par défaut) :
- `src/`, `app/`, `lib/`, `components/`, `pages/`, `api/`, `server/`, `client/`, `tests/`, `test/`, `__tests__/`, `e2e/`
- `node_modules/`, `.git/`, `.next/`, `dist/`, `build/`, `coverage/`, `.venv/`, `__pycache__/`
- `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `Cargo.toml`, `Cargo.lock`, `pyproject.toml`, `requirements*.txt`
- `.env.example`, `.env.template` (volontairement gardés)

### Mode `--deep` (opt-in)

Étend l'analyse au **code applicatif** :
- Modules jamais importés nulle part
- Exports déclarés mais jamais consommés
- Fichiers de tests pour du code qui n'existe plus

**Règle stricte en mode `--deep`** : aucune suppression auto-proposée pour du code. Toujours classer en ASK avec preuves (commandes grep exécutées, résultats vides). C'est à l'utilisateur de trancher.

Activation : l'utilisateur dit "deep", "complet", "code inclus", "tout le projet", "incluant le code", ou tape `/tidy --deep`.

## Prérequis vérifiés au démarrage

```bash
git rev-parse --show-toplevel
git status --short
```

Si pas de repo git : arrêter et expliquer que le skill repose sur `git mv` / `git log` / `git ls-files`.

Si `git status --short` n'est pas vide : afficher les fichiers modifiés/non-trackés et demander :

> Le repo a des changements non commités. Le skill va faire des `git mv` et `git rm` qui se mélangeront avec ton travail en cours. Tu préfères :
> 1. Commit ou stash d'abord (recommandé)
> 2. Continuer quand même (les changements seront mélangés)
> 3. Annuler

Suggérer également de créer une branche dédiée :

```bash
git checkout -b tidy/cleanup-$(date +%Y-%m-%d)
```

Mais ne pas l'imposer — certains projets travaillent direct sur main.

## Workflow

Six phases : **Inventaire → Classification → Audit sécurité → Rapport → Exécution séquentielle → Méta-mise à jour**.

### Phase 1 — Inventaire

Construis une vision complète du projet avant de juger quoi que ce soit.

**1.1 Cartographie globale**

```bash
# Structure (3 niveaux suffisent)
find . -maxdepth 3 -type d \
  -not -path '*/node_modules*' -not -path '*/.git*' \
  -not -path '*/dist*' -not -path '*/build*' \
  -not -path '*/.next*' -not -path '*/coverage*' \
  -not -path '*/__pycache__*' -not -path '*/.venv*' \
  | sort
```

**1.2 Lecture de la doctrine projet**

À lire intégralement (ces fichiers définissent ce qui est « officiel ») :
- `CLAUDE.md` (racine + sous-dossiers)
- `AGENTS.md`
- `README.md` (racine)
- `docs/README.md`, `docs/index.md` si présents
- `.github/CONTRIBUTING.md`, `CONTRIBUTING.md`

Note mentale : tout fichier explicitement référencé dans ces docs est **protégé** (jamais classé en DELETE ou ARCHIVE sans flag explicite).

**1.3 Inventaire des candidats**

```bash
# Tous les .md hors zones protégées
git ls-files '*.md' '*.MD' '*.markdown' '*.txt' 'NOTES*' 'PLAN*' 'TODO*' 'CHANGELOG*' \
  | grep -vE '^(node_modules/|\.git/|dist/|build/|\.next/|coverage/)'

# Scripts orphelins (hors src/, scripts/ structurés)
git ls-files '*.sh' '*.py' '*.mjs' \
  | grep -vE '^(src/|app/|lib/|tests?/|server/|client/|api/)'

# Configs potentiellement doublonnées
git ls-files | grep -E '\.(eslintrc|prettierrc|babelrc|jest\.config|vite\.config|webpack\.config|tsconfig)' | sort

# Snapshots / artefacts oubliés
git ls-files | grep -iE '(dump|snapshot|backup|\.bak$|\.old$|tmp-|temp-|scratch-|wip-|draft-)'
```

**1.4 Métadonnées par fichier candidat**

Pour chaque candidat, collecter en parallèle :

```bash
# Date du dernier commit qui a touché le fichier
git log -1 --format='%ai' -- "<file>"

# Date de création
git log --diff-filter=A --format='%ai' -- "<file>" | tail -1

# Auteur du dernier commit
git log -1 --format='%an' -- "<file>"

# Nombre de commits qui touchent ce fichier
git log --oneline -- "<file>" | wc -l
```

**1.5 Carte des références**

Pour chaque candidat, déterminer s'il est référencé ailleurs :

```bash
# Référence par nom (sans extension)
BASENAME=$(basename "<file>" .md)
git grep -l "$BASENAME" -- ':!<file>' 2>/dev/null

# Référence par chemin
git grep -l "<file>" -- ':!<file>' 2>/dev/null

# Liens markdown explicites
git grep -lE '\[.*\]\(.*<basename>.*\)' 2>/dev/null
```

Marque chaque candidat avec : `referenced=true/false`, `referenced_by=[liste]`.

### Phase 2 — Classification

Pour chaque candidat, attribue **une seule** étiquette parmi : `KEEP`, `MOVE`, `ARCHIVE`, `DELETE`, `ASK`.

#### Heuristiques de classification

**KEEP** (rien à faire) si **tout** ce qui suit est vrai :
- Référencé dans CLAUDE.md / README / AGENTS.md, OU dans le code applicatif
- Au bon emplacement selon sa nature (cf. table ci-dessous)
- Pas marqué « obsolete », « deprecated », « old » dans le contenu

**MOVE → `<path>`** si :
- Référencé et utile, MAIS mal placé
- Le bon emplacement existe ou peut être créé sans bruit
- Cible la convention du projet (cf. table)

**ARCHIVE → `docs/archives/<topic>/`** si **au moins un** :
- Document de plan/spec/RFC dont la feature est livrée (vérifiable via `git log --all --grep="<feature>"` + présence dans le code)
- Notes de debug d'un bug fixé (vérifier via commit message contenant « fix » + ref)
- Compte-rendu de débat / décision déjà appliquée
- Document daté avec timestamp > 90 jours, non référencé, mais avec valeur historique évidente (décisions techniques, RCAs)
- Plan abandonné explicitement (mention « scrapped », « abandonné », « pas retenu »)

**DELETE** (proposition, jamais auto) si **tous** :
- Aucune référence trouvée nulle part
- Nom évoque le scratch : `tmp-*`, `wip-*`, `scratch-*`, `test-output-*`, `dump-*`, `*.bak`, `*.old`
- Contenu trivial ou redondant avec un fichier KEEP
- Pas modifié depuis > 30 jours
- L'auteur reconnaît dans le contenu qu'il est jetable (« delete me », « temp », « to remove »)

**ASK** dans **tous les autres cas ambigus** :
- Doublons potentiels (`feature-x.md` + `feature-x-v2.md` + `feature-x-old.md`)
- Document récent non référencé (pourrait être un work-in-progress de l'utilisateur)
- Contenu dense mais sans signal clair d'utilité
- Tout cas où tu hésites entre deux catégories

**Règle d'or** : en doute → **ASK**, jamais DELETE. La friction d'une question est infiniment plus faible que celle d'une suppression injuste.

#### Table de bon emplacement

| Nature du fichier | Emplacement attendu |
|---|---|
| Doc d'architecture, décisions | `docs/architecture/` |
| Plans / specs / RFCs en cours | `docs/plans/` |
| Plans terminés (feature livrée) | `docs/archives/<topic>/` |
| Notes d'incident / debug terminé | `docs/archives/incidents/AAAA-MM-JJ-<slug>/` |
| Guides utilisateur / dev | `docs/guides/` |
| API reference générée | `docs/api/` |
| Scripts utilitaires permanents | `scripts/` |
| Scripts one-off historiques | `scripts/archive/` ou suppression si trivial |
| Configs de tools (eslint, prettier) | racine (convention de l'outil) |
| Anciennes configs remplacées | DELETE (vérifier qu'elles ne sont plus chargées) |
| Rapports tidy (ce skill) | `docs/tidy/report-AAAA-MM-JJ.md` |

**Important** : si le projet a déjà une convention différente mais cohérente (ex : `documentation/` au lieu de `docs/`), respecte-la. Détecte ça à la Phase 1.

#### Signaux dans le contenu

Lis les 30-50 premières lignes de chaque candidat. Indicateurs forts :

- **Plan livré** : présence de `Status: DONE`, `Closed`, `Shipped`, `✅ Completed`, `[x]` sur > 80% des TODO
- **Plan abandonné** : mots-clés « scrapped », « pas retenu », « abandoned », « obsolete »
- **Document encore actif** : mots-clés « in progress », « WIP », « TODO », `[ ]` non cochés, date récente
- **Doublon** : début identique à un autre fichier, ou même titre H1
- **Scratch** : moins de 20 lignes, formattage cassé, phrases incomplètes

### Phase 3 — Audit sécurité

Indépendant de la classification mais inclus dans le rapport.

**3.1 Fichiers d'environnement trackés**

```bash
git ls-files | grep -E '^(\.env(\.|$)|.*\.env$)' | grep -v '\.example$\|\.template$\|\.sample$'
```

Tout résultat = alerte critique. Recommander :
1. Ajouter au `.gitignore`
2. `git rm --cached <file>` (préserve le fichier local)
3. **Rotation impérative** des secrets contenus si le fichier a déjà été pushé (vérifier avec `git log -- <file>`)

**3.2 Scan de secrets dans tout le repo**

```bash
# Patterns à grep (un par appel, plus lisible que des alternations)
git grep -nE 'AKIA[0-9A-Z]{16}'                       # AWS Access Key
git grep -nE 'sk-ant-[A-Za-z0-9_-]{20,}'              # Anthropic
git grep -nE 'sk-[A-Za-z0-9]{40,}'                    # OpenAI
git grep -nE 'ghp_[A-Za-z0-9]{36}'                    # GitHub PAT
git grep -nE 'github_pat_[A-Za-z0-9_]{82}'            # GitHub fine-grained
git grep -nE 'xox[baprs]-[A-Za-z0-9-]{10,}'           # Slack
git grep -nE 'AIza[0-9A-Za-z_-]{35}'                  # Google API
git grep -nE 'eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.'  # JWT
git grep -nE -- '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'  # Private keys
git grep -nE '(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["'"'"'][^"'"'"']{8,}'  # Generic
git grep -nE '://[a-zA-Z0-9_.-]+:[^@/]+@[a-zA-Z0-9.-]+'  # URLs with creds
```

Pour chaque match :
- Identifier le fichier + ligne
- Vérifier si présent dans l'historique git : `git log -p -S '<extrait>' -- '<file>'`
- Classer en gravité : **CRITIQUE** (clé valide identifiable + dans l'historique pushé) / **HAUTE** (clé valide identifiable, local seulement) / **MOYENNE** (pattern suspect, peut être un faux positif)

**3.3 .gitignore audit**

Vérifier la présence de :

```
.env
.env.local
.env.production
.env.*.local
*.pem
*.key
id_rsa*
.DS_Store
node_modules/
__pycache__/
.venv/
```

Lister ce qui manque mais ne pas forcer — c'est une recommandation contextuelle.

**3.4 Limites à reconnaître**

Le skill fait un scan **best-effort**, pas un audit professionnel. Pour les projets sensibles, recommander dans le rapport l'usage d'outils dédiés :
- `gitleaks` pour le scan d'historique
- `trufflehog` pour la détection en profondeur
- GitHub secret scanning si le repo est sur GitHub

### Phase 4 — Composition du rapport

Crée `docs/tidy/` si absent, puis écris `docs/tidy/report-AAAA-MM-JJ.md` (utiliser la date du jour). Si un rapport du jour existe déjà, suffixe avec `-2`, `-3`, etc.

Structure stricte :

```markdown
# Tidy report — <date longue>

**Repo** : `<nom>`
**Branche** : `<branche>`
**Mode** : default | --deep
**Fichiers analysés** : <n>
**Propositions** : <X déplacements, Y archivages, Z suppressions, W alertes sécu, Q questions>

---

## 🗂️ Réorganisation (déplacements)

> Exécutés via `git mv`. Réversible avec `git mv` inverse.

### `<chemin/source.md>` → `<chemin/cible.md>`

**Pourquoi** : <raison concise, 1-2 phrases>
**Références à mettre à jour** : <liste de fichiers qui pointent vers l'ancien chemin, ou « aucune »>

```bash
git mv "<source>" "<cible>"
```

<répéter pour chaque déplacement>

---

## 📦 Archivage

> Déplacement vers `docs/archives/<topic>/`. Le fichier reste lisible, on déclare juste qu'il n'est plus actif.

### `<chemin/source.md>` → `docs/archives/<topic>/<nom>.md`

**Pourquoi** : <raison : feature livrée, débat clos, plan abandonné…>
**Preuves** :
- <commit sha qui livre la feature : « feat(x): … »>
- <ou : section du code qui implémente la décision>

```bash
mkdir -p "docs/archives/<topic>"
git mv "<source>" "docs/archives/<topic>/<nom>.md"
```

<répéter>

---

## 🗑️ Suppressions proposées

> ⚠️ Action irréversible (récupérable seulement via `git revert` ou `git reflog`).
> Chaque suppression demandera une confirmation explicite.

### `<chemin/file>`

**Pourquoi** : <raison>
**Vérifications effectuées** :
- Aucune référence trouvée : `git grep "<basename>"` → 0 résultat
- Dernier commit : <date>
- Contenu : <résumé en une ligne>

```bash
git rm "<file>"
```

<répéter>

---

## 🔐 Sécurité

### CRITIQUE — <titre>

**Fichier** : `<path>:<ligne>`
**Type** : <AWS key | Anthropic key | …>
**Dans l'historique git** : oui (commit `<sha>`, il y a <durée>) / non
**Action recommandée** :
1. <…>
2. <…>

<répéter pour chaque alerte, ordonnées par gravité>

---

## ❓ Questions en suspens

Décisions que je n'ai pas su trancher seul. Réponds dans la session, ce ne sera pas exécuté tant que tu ne valides pas.

### Q1 — `<file>`

**Situation** : <description neutre>
**Hypothèses** :
- (a) Garder tel quel — <conséquence>
- (b) Déplacer vers `<x>` — <conséquence>
- (c) Archiver — <conséquence>
- (d) Supprimer — <conséquence>

**Ma recommandation** : <a/b/c/d> parce que <raison>

<répéter>

---

## Plan d'exécution

Le skill va te proposer chaque catégorie séquentiellement :

1. ✅ Réorganisation (sûre, réversible facilement)
2. 📦 Archivage (sûre, réversible facilement)
3. 🗑️ Suppressions (irréversible — confirmation supplémentaire)
4. 🔐 Sécurité (action par action)
5. ❓ Questions (réponses dans la conversation)

Tu peux à chaque étape : **GO** (tout valider), **EDIT** (modifier la liste), **SKIP** (passer cette catégorie), **STOP** (arrêter complètement).
```

**Important** : ce rapport doit être **lisible seul**. Un humain ou une nouvelle session Claude qui l'ouvre dans 3 mois doit comprendre quoi a été proposé et pourquoi, même sans contexte.

### Phase 5 — Exécution séquentielle

Annonce le rapport :

> J'ai écrit le rapport dans `docs/tidy/report-AAAA-MM-JJ.md`. Lis-le si tu veux voir le détail, puis on attaque catégorie par catégorie.

Puis pour **chaque catégorie**, dans l'ordre : Réorganisation → Archivage → Suppressions → Sécurité → Questions.

**Format de demande d'approbation** (concis, sans répéter tout le rapport) :

```
🗂️ Réorganisation — <N> déplacements proposés

  1. docs-plans/auth-spec.md → docs/plans/auth-spec.md
  2. NOTES.md → docs/notes/general.md
  3. random-script.sh → scripts/archive/random-script.sh

GO pour exécuter tout, EDIT pour modifier, SKIP pour passer, STOP pour arrêter.
```

Si **GO** : exécuter les `git mv` un par un, vérifier le résultat, puis **mettre à jour les références** dans les autres fichiers (liens markdown brisés). Utilise `Edit` pour patcher chaque référence trouvée à la Phase 1.

Si **EDIT** : demander quels items retirer ou modifier (« retire le 2, change la cible du 3 vers X »), reformer la liste, redemander GO.

Si **SKIP** : passer à la catégorie suivante sans rien faire.

Si **STOP** : sauvegarder l'état actuel dans le rapport (marquer ce qui a été fait), terminer.

**Spécificité Suppressions** : confirmation double obligatoire.

```
🗑️ Suppressions — <N> fichiers à effacer

  1. tmp-debug-2025-11.md
  2. old-config.json.bak
  3. scratch-ideas.md

⚠️  Action irréversible (récupérable seulement via git history).
GO pour confirmer toutes les suppressions, EDIT, SKIP, STOP.
```

Si GO : `git rm` un par un, afficher confirmation après chaque.

**Spécificité Sécurité** : action par action (pas en bloc), parce que chaque alerte a sa propre remédiation.

```
🔐 Alerte 1/3 — CRITIQUE — Clé Anthropic exposée dans src/config.ts:12

Actions recommandées :
  (a) Déplacer vers .env, ajouter .env au .gitignore, charger via process.env
  (b) Juste signaler, je m'en occupe
  (c) Ignorer (faux positif)

Quelle action ?
```

Selon le choix, exécuter les `Edit` nécessaires. Toujours **rappeler la rotation** si la clé a été pushée.

**Spécificité Questions** : ne rien faire, juste relire les Q une par une dans la session et appliquer la décision de l'utilisateur en direct, en mettant à jour le rapport au fur et à mesure.

### Phase 6 — Méta-mise à jour

Après exécution complète :

**6.1 Mettre à jour les références cassées**

Pour chaque fichier déplacé, scanner les références qui pointaient vers l'ancien chemin (déjà identifiées à la Phase 1) et les patcher :

```bash
git grep -l "<ancien-chemin>" | while read f; do
  # Utilise Edit tool pour remplacer
done
```

**6.2 Mettre à jour CLAUDE.md et README si la structure a bougé**

Si :
- `docs/` a été créé ou restructuré significativement
- Des dossiers ont été renommés
- Le nombre de fichiers à la racine a beaucoup baissé

Alors proposer une mise à jour du `CLAUDE.md` racine pour refléter la nouvelle structure (section "Project layout" ou équivalent).

**Délégation** : si beaucoup de docs ont bougé, suggérer à l'utilisateur de lancer `/doc-sync` après pour une synchro plus complète.

**6.3 Mettre à jour le rapport**

Marque dans `docs/tidy/report-AAAA-MM-JJ.md` ce qui a été **fait** vs **passé** vs **modifié**, en ajoutant en haut :

```markdown
> **Exécuté le <timestamp>**
> Déplacements : X/Y appliqués
> Archivages : X/Y appliqués
> Suppressions : X/Y appliquées
> Sécurité : X/Y traitées
> Questions : X/Y résolues
```

**6.4 Suggestion de commit**

Proposer un commit conventionnel mais **ne pas committer automatiquement** :

```
chore(tidy): reorganize docs and archive completed plans

- Move <N> files to their proper location
- Archive <N> completed plans to docs/archives/
- Remove <N> obsolete scratch files
- Address <N> security findings

See docs/tidy/report-AAAA-MM-JJ.md for the full plan.
```

## Mode `--deep` — règles spécifiques

En plus du périmètre par défaut, analyse aussi le code applicatif :

**Détection des modules orphelins**

Pour chaque fichier de code dans `src/`, `app/`, `lib/` :

```bash
# Nom du module sans extension
NAME=$(basename "<file>" | sed 's/\.[^.]*$//')

# Cherche import explicite
git grep -lE "(import.*from.*['\"].*${NAME}['\"]|require\(['\"].*${NAME})" -- ':!<file>'

# Cherche import implicite (index.ts, barrel)
# Vérifier que le dossier parent n'a pas d'index.* qui exporte ce module
```

**Critères stricts pour proposition de suppression d'un fichier de code** :
1. Zero référence (import OU require OU re-export) trouvée
2. Pas mentionné dans `package.json` scripts, ni dans configs de build
3. Pas point d'entrée déclaré
4. Pas un fichier convention (`page.tsx`, `route.ts`, `layout.tsx` dans Next.js par exemple)

Si ces 4 conditions sont **toutes** réunies → classer en **ASK** (jamais DELETE auto). Joindre les commandes grep exécutées comme preuve dans le rapport.

**Conventions par framework** à respecter (ne jamais proposer la suppression de) :
- Next.js : `page.*`, `layout.*`, `route.*`, `loading.*`, `error.*`, `not-found.*`, `middleware.*`, `*.config.*`
- React Router : fichiers dans `routes/`
- Astro : `pages/*.astro`
- Remix : `routes/*`
- Python : `__init__.py`, `setup.py`, `conftest.py`
- Rust : `mod.rs`, `lib.rs`, `main.rs`

Si le framework n'est pas reconnu, être prudent et **toujours ASK**.

## Règles transversales

1. **Toujours `git mv`, jamais `mv`** — préserve l'historique de blame
2. **Toujours `git rm`, jamais `rm`** — propre dans l'index
3. **Jamais de force-push, jamais d'amend** — laisse l'historique tranquille
4. **Jamais supprimer sans approbation explicite** — DELETE est toujours une *proposition* dans le rapport
5. **Jamais toucher `.git/`, `node_modules/`, lockfiles** — hors périmètre absolu
6. **Respecter `.gitignore`** — un fichier ignoré n'est pas un candidat (sauf alerte sécu sur `.env`)
7. **Document protégé = jamais classé DELETE/ARCHIVE sans flag explicite** : tout fichier référencé dans `CLAUDE.md`, `README.md`, `AGENTS.md`
8. **En cas de doute = ASK** — jamais une décision unilatérale sur du contenu utilisateur
9. **Un rapport par exécution** — même si l'utilisateur lance `/tidy` deux fois dans la journée, suffixer (`-2`, `-3`)
10. **Ne pas commit automatiquement** — l'utilisateur garde la main sur le commit final
11. **Limites de batch** — si > 200 candidats, demander à l'utilisateur de restreindre le périmètre (option `--scope=docs` ou `--scope=root` à proposer) plutôt que de produire un rapport ingérable

## Sortie attendue

À la fin du skill, l'utilisateur a :
- Un rapport `docs/tidy/report-AAAA-MM-JJ.md` complet et historiquement préservé
- Une structure de projet plus propre et conforme aux conventions
- Un `docs/archives/` qui contient l'histoire technique du projet (pas un cimetière, une bibliothèque)
- Zero secret exposé connu
- Un commit prêt à pousser (proposé, pas exécuté)
- Une nouvelle session Claude qui ouvre le projet trouve immédiatement la doc pertinente

## Anti-patterns à éviter

- **Ne pas faire** : proposer un grand plan sans rapport écrit (l'utilisateur perd le contexte entre les approbations)
- **Ne pas faire** : tout exécuter d'un coup après une seule approbation globale (l'utilisateur veut voir par catégorie)
- **Ne pas faire** : supprimer un fichier sans preuve qu'il est non-référencé
- **Ne pas faire** : déplacer un fichier sans patcher les références qui pointent vers lui
- **Ne pas faire** : classer en ARCHIVE/DELETE un document mentionné dans CLAUDE.md
- **Ne pas faire** : confondre « ancien » et « obsolète » — un RCA d'il y a 2 ans est précieux, pas obsolète
- **Ne pas faire** : prétendre faire un audit sécurité complet — le scan est best-effort, le signaler dans le rapport
