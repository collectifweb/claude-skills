---
name: session-review
description: Fait reviewer la session Claude Code courante par Codex CLI pour valider que rien n'ait été manqué. Codex analyse échanges + diff git, produit rapport, Claude accepte/rejette. Trigger /session-review, "faire reviewer la session", "que codex valide", "vérifier que rien manqué".
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

**Override par l'utilisateur** : si l'utilisateur mentionne un modèle différent ou un niveau de raisonnement différent dans sa demande initiale (ex: "lance la review codex avec gpt-5.4", "utilise codex-mini pour aller vite", "fais-le sans xhigh", "reasoning normal", "plus rapide"), respecte ce choix au lieu du défaut. Détecte ces mentions naturellement dans la requête. Voir les niveaux disponibles dans la section "Lancement et suivi de codex" plus bas.

**Concrètement** : toutes les invocations de `codex exec` dans ce skill doivent inclure ces flags par défaut :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "PROMPT_ICI"
```

**Note sur `gpt-5.5`** : ce modèle requiert une authentification ChatGPT (pas API key). En cas d'erreur d'authentification, propose à l'utilisateur de basculer sur `gpt-5.4` ou `gpt-5.3-codex` comme fallback.

## Lancement et suivi de codex (RÈGLE CRITIQUE)

**Tous les appels `codex exec` dans ce skill DOIVENT être lancés en arrière-plan** avec `run_in_background: true` sur l'outil Bash. Jamais en foreground.

**Pourquoi** : codex exec prend typiquement 5 à 15 minutes (xhigh raisonne longtemps). Un appel Bash en foreground time out à 2 min par défaut (10 min max), retourne en erreur, et tu crois que codex a échoué alors qu'il tourne toujours. C'est la cause #1 des sessions où je dois être relancé manuellement après plusieurs heures de silence.

### Pattern de lancement obligatoire

Toujours rediriger stderr + stdout vers un log file, et lancer en background :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  --json \
  "PROMPT_ICI" > /tmp/codex-stream-{phase}.log 2>&1
```

Sur l'outil Bash : `run_in_background: true`. Note le `bash_id` retourné.

**Ne pas piper vers `tee`** quand le bash tourne en background — selon les hooks et le shell, le pipe peut détacher stdin et faire échouer codex silencieusement. Redirection simple `> log 2>&1` uniquement.

### Protocole de suivi obligatoire

1. **Annonce à l'utilisateur** :
   > "Codex lancé en arrière-plan (phase X). Je surveille sa progression et te tiens au courant toutes les 30-60s."

2. **Boucle de polling** (toutes les 30-60 secondes, jamais plus long) :
   - Vérifie si le fichier de sortie attendu existe : `ls -la {chemin-vers-fichier-codex.md} 2>/dev/null`
   - Si pas encore là, vérifie que le process codex tourne toujours : `pgrep -af "codex exec" | head -5`
   - Lis la fin du log : `tail -30 /tmp/codex-stream-{phase}.log` pour repérer activité (`reasoning`, `command_execution`, `agent_message`), erreurs, ou achèvement
   - Lis aussi la sortie stream du bash background (BashOutput sur le `bash_id`) au cas où
   - **Donne un status à l'utilisateur à chaque tour** : "Codex tourne toujours, X minutes écoulées, dernière activité : [extrait]." Même un status minimal suffit — l'objectif est que l'utilisateur sache que tu n'as pas oublié.

3. **Critère d'achèvement** : le fichier `.md` attendu existe ET sa taille est stable sur deux polls consécutifs (codex finalise parfois après que le fichier apparaisse). À ce moment, lis le fichier et passe à la suite.

4. **Si codex échoue ou disparaît du `pgrep`** sans avoir créé le fichier : lis le log complet, diagnostique (auth, sandbox, modèle indisponible, pipe cassé), signale à l'utilisateur et propose un fallback.

5. **Si codex tourne >20 minutes sans output dans le log** : signale-le à l'utilisateur et propose d'interrompre + relancer avec `model_reasoning_effort="high"` (plus rapide que `xhigh`).

### Anti-oubli (très important)

**Tant que la phase courante n'a pas son fichier `.md` complet, tu n'as PAS terminé.** Ne passe à aucune autre tâche. Ne réponds à aucune digression. Si l'utilisateur change de sujet pendant l'attente, réponds brièvement puis rappelle : "Codex tourne toujours sur la phase X, je reste en surveillance." Le silence prolongé entre lancement et lecture est le bug que ce protocole corrige — l'utilisateur a déjà perdu 3 heures à cause de ça dans une session précédente.

Si tu reviens dans la conversation après une compression de contexte ou un nouveau tour utilisateur, ta première action doit être de vérifier l'état du codex en cours (existence du fichier attendu + `pgrep` + tail du log) avant de continuer.

### Niveaux de reasoning effort disponibles

Du plus rapide au plus profond :
- `low` — rapide, analyse superficielle
- `medium` — défaut codex, équilibré
- `high` — profond, recommandé si `xhigh` est trop lent
- `xhigh` — maximum, défaut de ce skill (5-15 min typique)

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

Une fois `01-context.md` écrit, invoque codex avec le prompt prévu pour la review **en arrière-plan** (`run_in_background: true` sur l'outil Bash — c'est obligatoire, voir section "Lancement et suivi de codex"). Voir `references/codex-prompts.md` pour les prompts exacts.

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
)" > /tmp/codex-stream-review.log 2>&1
```

Codex va :
1. Lire le contexte préparé
2. Explorer activement le code du repo (ce qui a été modifié + ce qui pourrait être impacté)
3. Identifier ce qui a été manqué, oublié, mal fait, à risque
4. Écrire son rapport structuré dans `02-codex-report.md`

Applique strictement le **Protocole de suivi obligatoire** pendant l'attente : polling 30-60s du fichier `02-codex-report.md` + `/tmp/codex-stream-review.log` + status à l'utilisateur. Ne passe à la phase 3 que lorsque le fichier est complet et stable.

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

Relance codex avec le prompt d'objection **en arrière-plan** (`run_in_background: true`, voir section "Lancement et suivi de codex" et `references/codex-prompts.md`) :

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
)" > /tmp/codex-stream-replies.log 2>&1
```

Applique de nouveau le **Protocole de suivi obligatoire** : polling 30-60s de `05-codex-replies.md` + tail du log + status à l'utilisateur, jusqu'à fichier complet et stable.

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
