---
name: session-review
description: Fait reviewer la session Claude Code courante par Codex (CLI) pour valider que rien n'ait été manqué dans le travail effectué. Codex examine les échanges de la session et le diff git non-commité, produit un rapport d'observations et recommandations, que Claude analyse et accepte/rejette point par point. Si Claude a des objections, il les soumet à Codex pour une réponse finale. Utilise ce skill dès que l'utilisateur demande de "faire reviewer la session", "double-vérifier ce qui a été fait", "que codex valide la session", "review codex de la session", "vérifier que rien n'a été manqué", "faire une session review", ou tape la slash command `/session-review`. À utiliser à la fin d'une session de travail Claude Code, avant que l'utilisateur ne commit ou ne ferme la session, pour s'assurer qu'aucun point important n'a été oublié.
---

# Session Review

Ce skill fait intervenir Codex (CLI OpenAI) comme **double-vérificateur indépendant** de la session de travail courante. Codex examine ce qui s'est échangé entre toi (Claude) et l'utilisateur, ainsi que les modifications de code effectuées, puis produit un rapport d'observations et recommandations. Tu (Claude) analyses ensuite ce rapport et décides ce que tu acceptes ou rejettes, avec possibilité de soumettre des objections finales à Codex.

## Principe général

À la différence de `confront-codex` (qui valide un **plan** avant implémentation), ce skill intervient **après** une session de travail réelle. L'objectif :

- Vérifier qu'aucun aspect important n'a été manqué pendant la session
- Détecter les choses oubliées (tests, docs, edge cases, sécurité, perf, dépendances)
- Identifier les fragilités introduites par les changements de code
- Capturer les bonnes pratiques non respectées

L'utilisateur n'arbitre pas les désaccords directement. Toi (Claude) fais le tri parmi les recommandations de Codex et tiens position quand c'est justifié. L'utilisateur reçoit à la fin un rapport synthétique avec les actions recommandées.

## Prérequis vérifiés au démarrage

Avant de lancer le workflow, vérifie que `codex` est installé :

```bash
codex --version
```

Si la commande n'est pas trouvée, arrête-toi et explique à l'utilisateur qu'il faut installer la CLI Codex (pas seulement l'extension VSCode). Voir https://developers.openai.com/codex/cli pour l'installation.

Vérifie également que tu es dans un dépôt git :

```bash
git rev-parse --show-toplevel
```

Si pas de repo git, signale-le à l'utilisateur — ce skill repose sur le diff git pour identifier ce qui a été changé.

## Choix du modèle codex

Par défaut, ce skill utilise **`gpt-5.5`** avec **`model_reasoning_effort="xhigh"`** pour invoquer codex. Ce choix optimise pour la qualité du raisonnement critique, ce qui est exactement ce qu'on cherche dans une revue de code et de session.

**Override par l'utilisateur** : si l'utilisateur mentionne un modèle différent ou un niveau de raisonnement différent dans sa demande initiale (ex: "lance la review codex avec gpt-5.4", "utilise codex-mini pour aller vite", "fais-le sans xhigh", "reasoning normal", "plus rapide"), respecte ce choix au lieu du défaut. Détecte ces mentions naturellement dans la requête.

**Niveaux de reasoning effort disponibles** (du plus rapide au plus profond) :
- `low` — rapide, analyse superficielle
- `medium` — défaut codex, équilibré
- `high` — profond, recommandé si `xhigh` est trop lent
- `xhigh` — maximum, défaut de ce skill (peut prendre 5-15 min)

**Concrètement** : toutes les invocations de `codex exec` dans ce skill doivent inclure ces flags par défaut :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "PROMPT_ICI"
```

**Note sur `gpt-5.5`** : ce modèle requiert une authentification ChatGPT (pas API key). En cas d'erreur d'authentification, propose à l'utilisateur de basculer sur `gpt-5.4` ou `gpt-5.3-codex` comme fallback.

## Visibilité de la progression de codex

Quand codex tourne en mode `exec`, il streame sa progression sur **stderr**. Selon le client, cette progression peut être invisible. Utilise `--json` pour obtenir un flux JSON Lines structuré sur stdout :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  --json \
  "PROMPT_ICI" 2>&1 | tee /tmp/codex-stream.log
```

Avec `--json`, tu vois en direct : `reasoning`, `command_execution`, `file_change`, `agent_message`. Le `tee` garde une trace.

**Si codex semble bloqué** : 10-15 minutes en `xhigh` sur une session avec beaucoup de changements est normal. Au-delà de 20 minutes sans output, suggère à l'utilisateur d'interrompre (Ctrl+C) et de relancer avec `model_reasoning_effort="high"`.

## Structure des fichiers

Tous les artefacts vivent dans `docs/reviews/` à la racine du projet :

```
docs/reviews/
└── session-review-{slug}-YYYY-MM-DD-HHMM/
    ├── 01-context.md              # Contexte préparé par Claude pour Codex
    ├── 02-codex-report.md         # Rapport de Codex (observations + recommandations)
    ├── 03-claude-decisions.md     # Décisions de Claude (accepté/rejeté/à objecter)
    ├── 04-claude-objections.md    # (optionnel) Objections de Claude pour Codex
    ├── 05-codex-replies.md        # (optionnel) Réponses finales de Codex aux objections
    └── synthesis.md               # Synthèse finale pour l'utilisateur (actions à faire)
```

**Choix du slug** : avant de créer les fichiers, identifie un slug court qui décrit le travail de la session (ex: `auth-oauth-fix`, `dashboard-refacto`, `email-templates`). Si ce n'est pas évident depuis le contexte de la session, demande à l'utilisateur :

> "Comment veux-tu nommer cette review ? (un slug court, ex: `auth-oauth-fix`)"

Crée le dossier de review (en remplaçant `{slug}` par la valeur retenue) :

```bash
SLUG="auth-oauth-fix"  # exemple
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
REVIEW_DIR="docs/reviews/session-review-${SLUG}-${TIMESTAMP}"
mkdir -p "$REVIEW_DIR"
```

Mémorise ce chemin pour toute la suite du workflow.

## Phase 1 — Préparer le contexte pour Codex

Codex ne peut pas voir les échanges de la session courante. Tu dois lui préparer un fichier `01-context.md` qui rassemble tout ce qu'il doit examiner.

### 1.1 Identifier le fichier de session courant

Les conversations Claude Code sont stockées dans `~/.claude/projects/<chemin-projet-encodé>/*.jsonl`. Le chemin est encodé en remplaçant chaque caractère non alphanumérique par `-` :

```bash
PROJECT_DIR=$(pwd | sed 's|[^a-zA-Z0-9]|-|g')
SESSIONS_DIR="$HOME/.claude/projects/${PROJECT_DIR}"
```

La session courante = le `.jsonl` le plus récemment modifié dans ce dossier (puisque tu es en train d'y écrire) :

```bash
CURRENT_SESSION=$(ls -t "$SESSIONS_DIR"/*.jsonl 2>/dev/null | head -1)
echo "Session courante : $CURRENT_SESSION"
```

**Sanity check** : vérifie que ce fichier a été modifié dans les 10 dernières minutes :

```bash
find "$CURRENT_SESSION" -mmin -10
```

Si vide, il y a un risque de mauvaise détection. Liste les sessions récentes et demande à l'utilisateur de confirmer laquelle reviewer.

### 1.2 Extraire le résumé des échanges de la session

Voir `references/session-extraction.md` pour la procédure complète. En résumé : extraire les messages utilisateur et assistant pertinents avec `jq` ou `python3`, en limitant la longueur pour rester gérable côté tokens (codex aura à le lire).

### 1.3 Capturer le diff git non-commité

```bash
# État des changements
git status > /tmp/git-status.txt

# Diff complet des fichiers trackés modifiés
git diff > /tmp/git-diff-tracked.diff

# Diff des fichiers stagés (s'il y en a)
git diff --cached > /tmp/git-diff-staged.diff

# Liste des fichiers untracked
git ls-files --others --exclude-standard > /tmp/git-untracked.txt
```

Si les fichiers untracked existent et sont du code (pas du bruit), capture aussi leur contenu.

### 1.4 Composer `01-context.md`

Structure recommandée :

```markdown
# Contexte de la session à reviewer

## Métadonnées
- **Projet** : [nom du repo]
- **Branche** : [git branch courante]
- **Commit de base** : [git rev-parse HEAD]
- **Date** : [YYYY-MM-DD HH:MM]
- **Slug** : [slug retenu]

## Objectif initial de la session
[2-4 lignes décrivant ce que l'utilisateur cherchait à accomplir, extrait
des premiers messages]

## Résumé chronologique des échanges
[Liste structurée : demandes utilisateur → actions Claude → résultats]

## Décisions techniques prises
[Choix d'architecture, libs, patterns, etc. qui ont été actés pendant la session]

## Modifications de code (diff git non-commité)

### Fichiers modifiés (tracked)
[Coller le contenu de git-diff-tracked.diff ou résumer si trop long, avec
les portions clés]

### Fichiers stagés
[Idem]

### Nouveaux fichiers (untracked)
[Liste + contenu si raisonnable]

## Points que Claude identifie déjà comme à risque ou incomplets
[Auto-évaluation honnête : ce que tu sais ne pas avoir traité, ou que
tu as fait rapidement, ou qui mérite un second regard]
```

**Important sur l'auto-évaluation** : sois honnête. Plus tu déclares tes propres zones de doute, plus la review de Codex sera utile. Ne survends pas le travail.

Écris ce fichier dans `$REVIEW_DIR/01-context.md`.

## Phase 2 — Faire intervenir Codex pour la review

Une fois `01-context.md` écrit, invoque codex avec le prompt prévu pour la review. Voir `references/codex-prompts.md` pour les prompts exacts.

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  --json \
  "$(cat <<'EOF'
[Prompt review — voir references/codex-prompts.md]

Contexte à analyser : docs/reviews/session-review-{slug}-{timestamp}/01-context.md

Écris ton rapport complet dans : docs/reviews/session-review-{slug}-{timestamp}/02-codex-report.md
EOF
)" 2>&1 | tee /tmp/codex-stream-review.log
```

Codex va :
1. Lire le contexte préparé
2. Explorer activement le code du repo (ce qui a été modifié + ce qui pourrait être impacté)
3. Identifier ce qui a été manqué, oublié, mal fait, à risque
4. Écrire son rapport structuré dans `02-codex-report.md`

Cette opération peut prendre plusieurs minutes — c'est normal. Vérifie ensuite que le fichier a bien été créé.

## Phase 3 — Analyse par Claude

Lis attentivement `02-codex-report.md`. Pour chaque observation/recommandation de Codex, prends une décision parmi :

- **Acceptée** : Codex a raison, c'est une vraie omission ou amélioration. Tu reconnais et tu retiens cette action.
- **Rejetée** : Codex a tort (mauvaise compréhension du contexte, suggestion non pertinente, hors scope, etc.). Justifie pourquoi.
- **À objecter** : Tu n'es pas d'accord mais l'argument mérite d'être confronté à Codex pour avoir sa réponse. Tu n'es pas certain à 100% qu'il ait tort, ou tu veux qu'il précise/justifie.
- **Nuancée** : Tu acceptes partiellement. Précise quelle partie tu retiens et quelle partie tu écartes.

Écris ta réponse dans `$REVIEW_DIR/03-claude-decisions.md`. Structure :

```markdown
# Décisions de Claude sur le rapport de Codex

## Synthèse rapide
- Recommandations totales : N
- Acceptées : N
- Rejetées : N
- Nuancées : N
- À objecter : N

## Détail point par point

### [R1] Titre de la recommandation de Codex
**Statut** : Acceptée | Rejetée | Nuancée | À objecter
**Justification** : ...
**Action retenue** (si acceptée/nuancée) : ...

### [R2] ...
[...]
```

Numérote les recommandations en reprenant les références du rapport de Codex. Si Codex n'a pas numéroté, fais-le toi-même de façon cohérente.

**Sois rigoureux dans le tri** : ne rejette pas par paresse ou pour défendre l'ego. Mais ne valide pas non plus tout systématiquement — Codex peut avoir tort, et le retour critique a de la valeur.

## Phase 4 (optionnelle) — Objections soumises à Codex

Si dans `03-claude-decisions.md` tu as des points marqués **À objecter** (ou des rejets sur lesquels tu veux la réponse de Codex), enchaîne sur cette phase. Sinon, saute directement à la phase 5.

**Décide seul** si cette phase est utile :
- Si tu as 1+ point en "À objecter" → lance la phase
- Si tu as uniquement des rejets que tu juges évidents → skip
- Si tu as des rejets qui pourraient bénéficier d'un dernier regard de Codex → lance la phase

Tu n'as **pas** besoin de demander à l'utilisateur. Décide, agis, informe.

### 4.1 Rédiger les objections

Écris `$REVIEW_DIR/04-claude-objections.md` :

```markdown
# Objections de Claude

Pour chaque point ci-dessous, j'ai un désaccord ou une demande de précision.
Codex, je te demande de répondre en ligne par ligne.

## Objection sur [R3]
**Position de Codex** : [résumé de sa recommandation]
**Mon désaccord** : [argumentation technique]
**Question pour toi** : [ce que tu veux qu'il clarifie ou justifie]

## Objection sur [R7]
[...]
```

### 4.2 Faire répliquer Codex

Relance codex avec le prompt d'objection (voir `references/codex-prompts.md`) :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  --json \
  "$(cat <<'EOF'
[Prompt objections — voir references/codex-prompts.md]

Lis ces fichiers en ordre :
- docs/reviews/session-review-{slug}-{timestamp}/01-context.md
- docs/reviews/session-review-{slug}-{timestamp}/02-codex-report.md
- docs/reviews/session-review-{slug}-{timestamp}/03-claude-decisions.md
- docs/reviews/session-review-{slug}-{timestamp}/04-claude-objections.md

Réponds aux objections de Claude dans : docs/reviews/session-review-{slug}-{timestamp}/05-codex-replies.md
EOF
)" 2>&1 | tee /tmp/codex-stream-replies.log
```

### 4.3 Intégrer les réponses

Lis `05-codex-replies.md`. Pour chaque réponse :
- Si Codex te convainc → mets à jour `03-claude-decisions.md` (passe le point en "Acceptée" avec mention "après réponse de Codex")
- Si Codex ne te convainc pas → maintiens ton rejet, note-le

Note ces ajustements à la fin de `03-claude-decisions.md` dans une section :

```markdown
## Mise à jour après réponses de Codex

### [R3] — Reclassé : Rejetée → Acceptée
Après la réponse de Codex (voir 05-codex-replies.md, section R3),
sa précision sur [X] me convainc. J'ajuste donc ma position.

### [R7] — Maintenu en Rejetée
La réponse de Codex sur [Y] ne change pas ma position parce que [...]
```

**Ne fais qu'un round d'objections.** Pas de débat sans fin. Au-delà de ce round, c'est à toi de trancher seul.

## Phase 5 — Synthèse finale pour l'utilisateur

Écris `$REVIEW_DIR/synthesis.md`. Ce document est destiné à l'utilisateur — il doit être actionnable et lisible sans connaître les fichiers intermédiaires.

Structure :

```markdown
# Synthèse de la session review — {slug}

**Date** : YYYY-MM-DD HH:MM
**Travail reviewé** : [1-2 lignes décrivant la session]

## Verdict global
[2-4 lignes : la session est-elle prête à être commitée / mergée ? Y a-t-il
des blockers ? Des nice-to-have ? L'évaluation honnête de l'état actuel.]

## Actions recommandées (à faire avant de commit/merge)

### Critiques (à traiter)
- [ ] Action concrète 1 — pourquoi c'est important
- [ ] Action concrète 2 — pourquoi

### Importantes (à considérer fortement)
- [ ] Action concrète 3 — bénéfice attendu
- [ ] ...

### Nice-to-have (optionnel)
- [ ] Action concrète 4
- [ ] ...

## Recommandations écartées (avec justification courte)
- [R-X] Codex suggérait [Y], écarté parce que [raison concise]

## Pour aller plus loin
- Rapport complet de Codex : `02-codex-report.md`
- Détail des décisions : `03-claude-decisions.md`
- [Si phase 4 a eu lieu] Échange d'objections : `04-claude-objections.md` + `05-codex-replies.md`
```

**Importance des actions concrètes** : chaque coche doit être actionnable directement. Pas de "améliorer la sécurité" mais "ajouter une validation `email_format` dans `auth/register.ts:42`". L'utilisateur doit pouvoir cocher en faisant le travail.

## Annonce finale à l'utilisateur

Quand `synthesis.md` est écrit, signale-le clairement :

```
✅ Review de session terminée.

Synthèse : docs/reviews/session-review-{slug}-{timestamp}/synthesis.md

Verdict : [recopie en 1-2 lignes le verdict global]

Actions critiques : N
Actions importantes : N
Nice-to-have : N

[Si phase 4 a eu lieu]
J'ai eu N objections sur des points de Codex. Après sa réponse :
- N reclassées en Acceptée
- N maintenues en Rejetée

Tu veux que je commence à traiter les actions critiques ?
```

Si la phase 4 n'a pas eu lieu, mentionne juste : "Pas d'objections sur les recommandations de Codex — j'ai accepté/rejeté chaque point sans avoir besoin de le challenger."

## Pour aller plus loin

- `references/session-extraction.md` — Comment extraire les échanges de la session courante
- `references/codex-prompts.md` — Prompts exacts à passer à codex pour chaque phase
- `references/exemples.md` — Exemples de bons rapports de review et de bonnes décisions de Claude
