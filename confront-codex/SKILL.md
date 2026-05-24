---
name: confront-codex
description: Confronte un plan technique avec Codex CLI via débats itératifs jusqu'au consensus. Plan final dans docs/, rounds archivés. Trigger /confront-codex, "confronter codex", "valider le plan avec codex", "challenger l'approche", "second avis sur le plan".
---

# Confront-Codex

Ce skill orchestre un débat structuré entre Claude (toi) et Codex (CLI OpenAI) sur un plan technique, jusqu'à consensus. L'utilisateur arbitre les cas où le débat s'enlise.

## Principe général

L'utilisateur a élaboré un plan avec toi (typiquement en plan mode). Plutôt que de l'exécuter directement, il veut une seconde paire d'yeux indépendante. Codex va lire ton plan, le challenger, et tu vas lui répondre. Cycle itératif jusqu'à accord.

L'objectif n'est PAS de faire céder un camp à tout prix. C'est un vrai débat technique : tu peux être convaincu, ou tenir ta position si tu as de bons arguments. Le consensus émerge soit parce que l'un des deux convainc l'autre, soit parce que les deux trouvent une troisième voie meilleure que les positions initiales.

## Prérequis vérifiés au démarrage

Avant de lancer le workflow, vérifie que `codex` est installé :

```bash
codex --version
```

Si la commande n'est pas trouvée, arrête-toi et explique à l'utilisateur qu'il faut installer la CLI Codex (pas seulement l'extension VSCode). Voir https://developers.openai.com/codex/cli pour l'installation.

## Choix du modèle codex

Par défaut, ce skill utilise **`gpt-5.5`** avec **`model_reasoning_effort="xhigh"`** pour invoquer codex. Ce choix optimise pour la qualité du raisonnement critique, ce qui est exactement ce qu'on cherche dans une revue de plan technique.

**Override par l'utilisateur** : Si l'utilisateur mentionne un modèle différent dans sa demande initiale (ex: "lance la confrontation codex avec gpt-5.4", "utilise codex-mini pour aller vite", "fais-le sans xhigh"), respecte ce choix au lieu du défaut. Détecte ces mentions naturellement dans la requête.

**Concrètement** : toutes les invocations de `codex exec` dans ce skill doivent inclure ces flags par défaut, **plus la redirection stdin et le log de sortie** (voir section "Lancement et suivi de codex" plus bas pour le détail) :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "PROMPT_ICI" > /tmp/codex-confront-{slug}-{phase}.log 2>&1 < /dev/null
```

Si l'utilisateur demande un modèle différent, remplace `gpt-5.5` par le modèle demandé. Si l'utilisateur dit explicitement "sans xhigh" ou "reasoning normal", retire le flag `-c model_reasoning_effort="xhigh"`. **Ne jamais** retirer `< /dev/null` ni ajouter `--json`.

**Note sur `gpt-5.5`** : ce modèle requiert une authentification ChatGPT (pas API key). Si tu obtiens une erreur d'authentification, signale-le à l'utilisateur et propose de basculer sur `gpt-5.4` ou `gpt-5.3-codex` comme fallback.

## Lancement et suivi de codex (RÈGLE CRITIQUE)

**Tous les appels `codex exec` dans ce skill DOIVENT être lancés en arrière-plan** avec `run_in_background: true` sur l'outil Bash. Jamais en foreground.

**Pourquoi** : codex exec prend typiquement 3 à 15 minutes (xhigh raisonne longtemps). Un appel Bash en foreground time out à 2 min par défaut (10 min max), retourne en erreur, et tu crois que codex a échoué alors qu'il tourne toujours. C'est l'une des deux causes du bug où l'utilisateur doit me relancer manuellement après 10+ minutes de silence.

### Piège stdin (deuxième cause du bug)

Codex en mode exec lit stdin par défaut. Le shell de Claude Code lui passe un stdin "ouvert mais vide" → codex bloque indéfiniment sur `Reading additional input from stdin...` sans jamais commencer son travail. Le process apparaît dans `pgrep`, semble vivant, mais ne fait rien.

**Deux mitigations obligatoires** sur chaque invocation :

1. **Toujours rediriger stdin depuis `/dev/null`** en fin de commande : `... "PROMPT" < /dev/null`
2. **Ne jamais utiliser le flag `--json`** dans ce skill — il aggrave le bug stdin et n'apporte rien pour ce workflow (on n'a pas besoin de parser un stream JSON, on lit juste le fichier `.md` produit à la fin).

### Pattern de lancement obligatoire

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "PROMPT_ICI" > /tmp/codex-confront-{slug}-{round}.log 2>&1 < /dev/null
```

Lancer avec `run_in_background: true` sur l'outil Bash. Noter le `bash_id` retourné.

### Protocole de suivi obligatoire (polling ACTIF)

**Le harness Claude Code ne te notifie PAS automatiquement quand codex se bloque ou hang.** Il ne notifie que sur completion réelle du process. Si codex hang sur stdin, tu peux attendre des heures sans aucune notification. Tu dois donc poller activement — appeler toi-même les commandes ci-dessous, pas attendre passivement.

**À chaque tour (toutes les 30-60 secondes, pas plus long)** :

1. Vérifie si le fichier de sortie existe et grandit : `ls -la {chemin-vers-round-N-codex.md} 2>/dev/null`
2. Vérifie que le process codex tourne toujours : `pgrep -af "codex exec" | head -5`
3. Lis la fin du log : `tail -40 /tmp/codex-confront-{slug}-{round}.log` pour repérer activité (`reasoning`, `command_execution`, `agent_message`), erreurs (`auth`, `stdin`), ou achèvement
4. Lis aussi la sortie du bash background (BashOutput sur le `bash_id`) en complément
5. **Donne un status à l'utilisateur à chaque tour** : "Codex tourne, X min écoulées, dernière activité : [extrait]." Même un status minimal suffit — l'objectif est que l'utilisateur sache que tu n'as pas oublié.

### Détection du hang stdin

Si après 2-3 polls (1-3 min) :
- `pgrep` montre codex vivant
- ET le log contient `Reading additional input from stdin` ou reste vide / strictement identique au lancement
- ET aucun fichier `.md` n'apparaît

→ **c'est un hang stdin**. Kill le process (`pkill -f "codex exec"`), relance en t'assurant que `< /dev/null` est bien présent et que `--json` est absent. Signale-le à l'utilisateur.

### Critère d'achèvement

Le fichier `round-N-codex.md` existe ET sa taille est stable sur deux polls consécutifs (codex finalise parfois après que le fichier apparaisse). À ce moment, lis le fichier et passe à la suite.

### Si codex échoue ou disparaît du `pgrep` sans avoir créé le fichier

Lis le log complet, diagnostique (auth, sandbox, modèle indisponible, hang stdin), signale à l'utilisateur et propose un fallback.

### Anti-passivité (très important)

**Le harness ne te re-invoque pas tout seul à intervalle régulier.** Quand tu dis "Je vais poller toutes les 60s" ou "Je serai re-invoqué automatiquement", c'est faux si tu attends passivement — tu restes silencieux jusqu'à la prochaine action utilisateur. Tu dois enchaîner les commandes Bash de polling toi-même, dans une boucle active de tours consécutifs, jusqu'à ce que le critère d'achèvement soit rempli ou qu'un hang soit détecté.

**Tant que le round courant n'a pas son fichier `round-N-codex.md` complet, tu n'as PAS terminé.** Ne passe à aucune autre tâche. Ne réponds à aucune digression. Si l'utilisateur change de sujet pendant l'attente, réponds brièvement puis rappelle : "Codex tourne toujours sur le round N, je reste en surveillance." Si tu reviens après une compression de contexte ou un nouveau tour utilisateur, ta première action doit être de vérifier l'état du codex en cours (existence du fichier attendu + `pgrep` + tail du log) avant de continuer.

## Structure des fichiers

Tous les échanges vivent dans `docs/` à la racine du projet :

```
docs/
├── plan-{slug-feature}.md           # Le consensus final (output du skill)
└── archives/
    └── confront-codex-{slug-feature}-YYYY-MM-DD-HHMM/
        ├── round-1-claude.md         # Ton plan initial
        ├── round-1-codex.md          # Première analyse de Codex
        ├── round-2-claude.md         # Ta réponse aux critiques
        ├── round-2-codex.md          # Contre-réponse de Codex
        └── ... (autant de rounds que nécessaire)
```

**Choix du slug** : Avant de créer les fichiers, identifie un slug court qui décrit la feature/le plan (ex: `auth-oauth`, `migration-postgres`, `refacto-stores`). Si ce n'est pas évident depuis le contexte, demande à l'utilisateur :

> "Comment veux-tu nommer ce plan ? (un slug court, ex: `auth-oauth`)"

Le timestamp sur le dossier d'archive permet de garder l'historique même si tu refais une session de confrontation sur la même feature plus tard.

Crée le dossier d'archive (en remplaçant `{slug}` par la valeur retenue) :

```bash
SLUG="auth-oauth"  # exemple
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
ARCHIVE_DIR="docs/archives/confront-codex-${SLUG}-${TIMESTAMP}"
mkdir -p "$ARCHIVE_DIR"
```

Mémorise le chemin du dossier d'archive et le slug — tu vas y écrire tous les rounds.

## Le workflow round par round

### Round 1 : Ton plan initial

Rédige ton plan dans `docs/archives/confront-codex-{timestamp}/round-1-claude.md`. Le plan doit contenir :

1. **Contexte** — Quel problème on résout, dans quel projet, quelles contraintes
2. **Approche proposée** — Les choix d'architecture, technos, pattern
3. **Étapes d'implémentation** — Découpées clairement
4. **Points sensibles** — Ce que tu identifies comme risqué ou discutable
5. **Alternatives écartées** — Pourquoi tu n'as pas choisi telle ou telle autre voie

Important : écris ce document en sachant qu'il sera challengé. Ne survends pas, ne cache pas les zones d'incertitude. Plus tu es honnête sur les faiblesses, plus le débat sera utile.

### Round 1 : Faire intervenir Codex

Une fois `round-1-claude.md` écrit, invoque codex avec le prompt prévu pour cette première analyse. Voir `references/codex-prompts.md` pour les prompts exacts à utiliser.

```bash
cat references/codex-prompts.md  # Si nécessaire pour récupérer les prompts
```

Lance codex en mode non-interactif **avec `run_in_background: true`** (voir section "Lancement et suivi de codex" — c'est obligatoire) :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "$(cat <<'EOF'
[Prompt round-1 — voir references/codex-prompts.md]

Plan à analyser : docs/archives/confront-codex-{slug}-{timestamp}/round-1-claude.md

Écris ton analyse complète dans : docs/archives/confront-codex-{slug}-{timestamp}/round-1-codex.md
EOF
)" > /tmp/codex-confront-{slug}-r1.log 2>&1 < /dev/null
```

⚠️ `< /dev/null` en fin de commande est obligatoire (anti-hang stdin). Pas de `--json`. Voir section "Lancement et suivi de codex" pour le détail.

Une fois lancé en arrière-plan, applique strictement le **Protocole de suivi obligatoire** (polling actif 30-60s, status à l'utilisateur, détection hang stdin, critère d'achèvement). Ne passe au round suivant qu'une fois `round-1-codex.md` complet et stable.

### Round N (N≥2) : Ta réponse

Lis le fichier de codex du round précédent. Pour chaque point qu'il soulève :

- **S'il a raison** : reconnais-le explicitement, ajuste ton plan, explique ce qui change
- **S'il a tort ou que tu n'es pas d'accord** : explique pourquoi, avec arguments techniques, sans complaisance ni agressivité
- **Si c'est nuancé** : expose la nuance honnêtement, propose éventuellement une voie médiane

Écris ta réponse dans `round-N-claude.md`. Structure recommandée :

```markdown
# Round N — Réponse à Codex

## Points où je rejoins Codex
- [Point X] : Codex a raison parce que... J'ajuste donc le plan ainsi : ...

## Points où je tiens ma position
- [Point Y] : Je maintiens parce que... L'argument de Codex ne tient pas parce que...

## Points où je propose une voie alternative
- [Point Z] : Ni ma version initiale ni celle de Codex. Je propose plutôt...

## Plan ajusté (état actuel)
[Le plan dans son état actuel, intégrant les ajustements acceptés]
```

### Round N : Faire répliquer Codex

Relance codex avec le prompt de round suivant (voir `references/codex-prompts.md`), **toujours avec `run_in_background: true`**. Codex doit lire le dernier fichier de toi et ses propres analyses précédentes pour rester cohérent.

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "$(cat <<'EOF'
[Prompt round-N — voir references/codex-prompts.md]

Lis ces fichiers en ordre :
- docs/archives/confront-codex-{slug}-{timestamp}/round-1-claude.md
- docs/archives/confront-codex-{slug}-{timestamp}/round-1-codex.md
- ... (tous les rounds précédents)
- docs/archives/confront-codex-{slug}-{timestamp}/round-N-claude.md (le plus récent)

Écris ta contre-réponse dans : docs/archives/confront-codex-{slug}-{timestamp}/round-N-codex.md
EOF
)" > /tmp/codex-confront-{slug}-r{N}.log 2>&1 < /dev/null
```

⚠️ `< /dev/null` obligatoire, pas de `--json`.

Applique de nouveau le **Protocole de suivi obligatoire** pendant l'attente.

## Détection du consensus (BILATÉRAL OBLIGATOIRE)

**Règle fondamentale** : tu ne peux JAMAIS déclarer le consensus unilatéralement. Le consensus n'existe que si **Codex ET toi** l'avez explicitement validé dans un même round. Tant que ce n'est pas le cas, les rounds continuent.

### Le token de consensus

À chaque round à partir du round 2, Codex doit terminer son fichier par exactement une de ces deux lignes (les prompts dans `references/codex-prompts.md` l'exigent) :

- `CONSENSUS_ATTEINT` — Codex confirme qu'aucun désaccord substantiel ne subsiste, le plan est validé en l'état.
- `CONSENSUS_REFUSE` — Au moins un point reste en débat ou un manque subsiste.

Ta première action après lecture du fichier de Codex est de **chercher ce token en fin de document** (`grep -E '^(CONSENSUS_ATTEINT|CONSENSUS_REFUSE)$' round-N-codex.md`). Si le token est absent, le round est invalide et tu dois relancer codex pour qu'il l'ajoute explicitement.

### Détermination du consensus

**Le consensus est atteint UNIQUEMENT si les deux conditions suivantes sont vraies au même round** :

1. Le fichier de codex se termine par `CONSENSUS_ATTEINT`
2. Tu rédiges un fichier `round-N-claude.md` final (post-codex) où tu écris explicitement : "Je confirme également le consensus, plus aucun désaccord substantiel de mon côté" — avec ta propre revue du plan finalisé.

Tu peux donc avoir trois cas en lisant le `CONSENSUS_ATTEINT` de Codex :
- **Tu es d'accord** : rédige ton `round-N-claude-confirm.md` confirmant, puis produis le plan final.
- **Tu n'es pas d'accord** (il te reste des objections que Codex n'a pas adressées) : rédige `round-N+1-claude.md` listant tes points restants, relance un round codex. Le consensus n'est PAS atteint.
- **Tu hésites** : remonte à l'utilisateur l'écart de perception avant de continuer.

Symétriquement, si Codex écrit `CONSENSUS_REFUSE`, tu continues les rounds même si toi tu pensais qu'on avait fini.

### Continue les rounds tant que :
- Au moins l'un des deux camps a un `CONSENSUS_REFUSE` ouvert
- OU Codex désapprouve un élément du plan
- OU Codex pointe un manque que tu n'as pas adressé
- OU Codex propose une amélioration que tu n'as ni acceptée ni explicitement rejetée avec arguments
- OU toi tu identifies un point que Codex n'a pas suffisamment traité

### Demande à l'utilisateur d'arbitrer si :
- Le débat tourne en rond (3 rounds sans progression réelle sur le ou les mêmes points)
- Codex et toi êtes en désaccord ferme sur un point structurel sans qu'aucun argument ne semble pouvoir convaincre l'autre
- **Tu as atteint 5 rounds** : à ce stade, stop systématique. Présente l'état du débat à l'utilisateur et demande comment trancher. Au-delà, le coût (temps, tokens codex) devient disproportionné par rapport au gain marginal.

Quand tu hésites, formule clairement à l'utilisateur :
- Ce qui reste en débat
- Ta position et celle de Codex
- Ce que tu recommandes (continuer / arrêter / trancher manuellement)

## Communication avec l'utilisateur entre les rounds

Après chaque round complet (toi + codex), donne un bref status :

```
Round N terminé.
- Points sur lesquels Codex et moi sommes d'accord : ...
- Points encore en débat : ...
- Mon évaluation : on continue / on arrête / je te laisse trancher

Je lance le round N+1 ?
```

Tu n'es pas obligé de demander à chaque round si l'utilisateur veut continuer — si la progression est claire, enchaîne. Demande explicitement s'il y a une décision à arbitrer ou si tu hésites.

## Production du plan final consolidé

Une fois le consensus bilatéral confirmé (`CONSENSUS_ATTEINT` côté Codex + confirmation explicite côté Claude dans le `round-N-claude-confirm.md`), écris `docs/plan-{slug}.md` (en utilisant le même slug que pour le dossier d'archive). Ce document doit être :

- **Autonome** : lisible sans connaître l'historique du débat. Quelqu'un qui arrive frais doit pouvoir l'exécuter.
- **Propre** : pas de "Codex a dit que...", pas de traces du débat. Juste le plan final tel qu'il est maintenant.
- **Complet** : contexte, approche, étapes, points sensibles à surveiller pendant l'implémentation.

Structure recommandée :

```markdown
# Plan : [Nom de la feature/du projet]

## Contexte
[Le problème qu'on résout]

## Approche
[L'architecture finale, les choix techniques]

## Étapes d'implémentation
1. ...
2. ...

## Points de vigilance
[Ce qu'il faut surveiller, qui a émergé du débat]

## Décisions explicitement écartées
[Brèves justifications des alternatives non retenues — utile pour le futur]
```

Les fichiers de rounds restent dans `docs/archives/confront-codex-{slug}-{timestamp}/` — ils servent de mémoire si on veut comprendre plus tard pourquoi telle décision a été prise.

## Annonce finale à l'utilisateur

Quand le `plan-{slug}.md` est écrit, signale-le clairement :

```
✅ Consensus atteint après N rounds.

Plan final : docs/plan-{slug}.md
Historique du débat : docs/archives/confront-codex-{slug}-{timestamp}/

Prêt à exécuter le plan ?
```

## Pour aller plus loin

- `references/codex-prompts.md` — Prompts exacts à passer à codex pour chaque round
- `references/exemples.md` — Exemples de bons et mauvais débats pour calibrer ton ton
