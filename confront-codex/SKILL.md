---
name: confront-codex
description: Confronte un plan technique avec un second agent indépendant (Codex depuis Claude, Claude depuis Codex, ou Fable avec --fable) par débats itératifs jusqu'au consensus. Plan final dans docs/, rounds archivés. Option --model pour choisir le modèle. Trigger /confront-codex, "confronter codex", "valider le plan avec codex", "challenger l'approche", "second avis sur le plan".
---

# Confront-Codex

Ce skill orchestre un débat structuré entre toi et un second agent indépendant (Codex si tu es Claude, Claude si tu es Codex, Fable sur demande) sur un plan technique, jusqu'à consensus. L'utilisateur arbitre les cas où le débat s'enlise.

## Principe général

L'utilisateur a élaboré un plan avec toi (typiquement en mode plan). Plutôt que de l'exécuter directement, il veut une seconde paire d'yeux indépendante. L'autre va lire ton plan, le challenger, et tu vas lui répondre. Cycle itératif jusqu'à accord.

L'objectif n'est PAS de faire céder un camp à tout prix. C'est un vrai débat technique : tu peux être convaincu, ou tenir ta position si tu as de bons arguments. Le consensus émerge soit parce que l'un des deux convainc l'autre, soit parce que les deux trouvent une troisième voie meilleure que les positions initiales.

## Qui confronte qui

Le skill oppose l'agent qui le lance à un second agent, indépendant :

| Le skill tourne dans | Second avis | Commande |
|---|---|---|
| Claude Code | Codex | `codex exec` |
| Codex CLI | Claude | `claude -p` |
| l'un ou l'autre, avec `--fable` (ou « avec Fable ») | Fable | `claude -p --model fable` |

Dans ce document, **toi** désigne l'agent qui lance le skill et **l'autre** le second avis. Chaque fichier de round porte le nom de l'agent qui l'a écrit (`round-N-claude.md`, `round-N-codex.md`, `round-N-fable.md`).

Au démarrage, vérifie que la commande de l'autre existe (`codex --version` ou `claude --version`). Si l'utilisateur n'a rien précisé, c'est la ligne par défaut du tableau ; `--fable` ou « avec Fable » choisit Fable. Si elle manque, arrête-toi et explique qu'il faut installer la CLI (pour Codex : https://developers.openai.com/codex/cli, pas seulement l'extension VS Code).

## Choix du modèle (second avis = Codex)

- **Défaut** : `gpt-5.6-sol` avec `model_reasoning_effort="xhigh"`.
- **Secours**, seulement si le modèle est refusé : `gpt-5.6-terra`, puis `gpt-5.6-luna`. Ne jamais basculer tout seul vers un modèle plus cher (`gpt-6-astra`, `gpt-5.5`) : ça reste le choix explicite de l'utilisateur. Signale chaque bascule.
- **Modèle refusé** : une CLI Codex trop ancienne refuse les modèles récents, parfois avec un message trompeur. Constaté le 23 sept. 2026 : la 0.148.0 répondait « not supported when using Codex with a ChatGPT account » pour `gpt-6-sol`, que la 0.156.1 accepte sur le même compte. Avant de basculer sur un secours, vérifie `codex --version` et signale une éventuelle mise à jour ; cite toujours le message d'erreur tel quel.
- **Choix de l'utilisateur** : `/confront-codex --model <nom>`, ou le modèle cité en langage naturel (« avec astra », « en 5.6 sol »). L'utilisateur écrit souvent le nom approximativement (`gpt6astra`, `6 astra`, `5,6-sol`). Retrouve le vrai identifiant dans la liste des modèles de Codex :

  ```bash
  python3 -c 'import json,os;[print(m["slug"],"-",m["description"]) for m in json.load(open(os.path.expanduser("~/.codex/models_cache.json")))["models"] if m.get("visibility")=="list"]'
  ```

  Compare sans tenir compte des tirets, points, espaces et majuscules. Une seule correspondance : annonce-la en une ligne (« Modèle retenu : gpt-6-astra ») et lance. Plusieurs (« sol » vise `gpt-6-sol` et `gpt-5.6-sol`) : demande laquelle. Aucune, ou fichier absent : dis-le et propose la liste.
- **Raisonnement** : « sans xhigh » ou « reasoning normal » retire `-c model_reasoning_effort="xhigh"`. « reasoning high » le remplace par `high`.

Quand l'autre est Claude, n'impose pas de modèle : `claude -p` prend celui configuré, sauf si l'utilisateur en demande un (`--model <nom>` : `opus`, `sonnet`, `haiku`, `fable` ou un identifiant complet). Avec `--fable`, c'est `--model fable`.

## Lancer l'autre et attendre sa réponse

L'autre met typiquement 3 à 15 minutes à répondre. Sa **réponse finale** est l'analyse du round : elle est enregistrée directement dans le fichier du round. L'autre n'écrit aucun fichier lui-même et tourne en lecture seule, ce qui l'empêche de modifier le projet.

**Second avis = Codex** :

```bash
timeout 45m codex exec \
  --model gpt-5.6-sol \
  -c model_reasoning_effort="xhigh" \
  --sandbox read-only \
  --skip-git-repo-check \
  -o "$ARCHIVE_DIR/round-N-codex.md" \
  "PROMPT" > /tmp/confront-{slug}-rN.log 2>&1 < /dev/null
```

**Second avis = Claude ou Fable** (`round-N-claude.md` ou `round-N-fable.md`) :

```bash
# Fable : garder --model fable et écrire round-N-fable.md
# Claude : retirer la ligne --model (ou mettre le modèle demandé) et écrire round-N-claude.md
timeout 45m claude -p "PROMPT" \
  --allowedTools=Read,Grep,Glob \
  --model fable \
  > "$ARCHIVE_DIR/round-N-fable.md" 2> /tmp/confront-{slug}-rN.log < /dev/null
```

Le prompt vient **juste après `-p`**, et `--allowedTools` s'écrit avec `=` : sous la forme `--allowedTools "Read,Grep,Glob" "PROMPT"`, l'option avale le prompt et la commande échoue (« Input must be provided »). Seuls ces trois outils de lecture sont permis : toute écriture reste en attente d'une approbation qui ne vient jamais, donc rien n'est modifié.

Trois règles, chacune pour une panne déjà vécue :

- **`< /dev/null` toujours.** Sans lui, `codex exec` attend une saisie qui ne vient jamais (`Reading additional input from stdin...`) et reste bloqué indéfiniment. Pas de `--json` non plus.
- **`timeout 45m` toujours.** Quoi qu'il arrive (réussite, erreur, blocage), la commande finit par se terminer. Aucune attente sans fin. Sur macOS, `timeout` s'appelle `gtimeout` (paquet `coreutils` de Homebrew).
- **En arrière-plan.** Dans Claude Code, lance la commande avec `run_in_background: true` : tu es relancé automatiquement quand elle se termine. En premier plan, l'outil coupe au bout de 10 minutes maximum, et tu croirais à un échec alors que l'autre travaille encore. Dans Codex, lance-la de la façon qui permet d'attendre 45 minutes, puis relis le fichier.

Pendant l'attente, dis à l'utilisateur que l'autre tourne et termine ton tour : ne boucle pas en vérifiant sans arrêt. S'il te relance entre-temps, fais le point avec `tail -20` du journal.

**À la fin de la commande** :

- Code 0 et fichier du round non vide : lis-le et passe à la suite.
- Code 124 : le délai de 45 minutes est dépassé. Montre la fin du journal et demande s'il faut relancer.
- Autre code : lis le journal, identifie la cause (authentification, modèle refusé, bac à sable) et applique le secours du modèle, ou signale le problème.

## Structure des fichiers

Tous les échanges vivent dans `docs/` à la racine du projet (exemple quand tu es Claude et l'autre Codex) :

```
docs/
├── plan-{slug}.md                     # Le consensus final (sortie du skill)
└── archives/
    └── confront-codex-{slug}-YYYY-MM-DD-HHMM/
        ├── round-1-claude.md          # Ton plan initial
        ├── round-1-codex.md           # Première analyse de l'autre
        ├── round-2-claude.md          # Ta réponse aux critiques
        ├── round-2-codex.md           # Contre-réponse de l'autre
        ├── ...                        # Autant de rounds que nécessaire
        └── round-N-claude-confirm.md  # Ta confirmation du consensus
```

**Choix du slug** : avant de créer les fichiers, identifie un slug court qui décrit le plan (ex : `auth-oauth`, `migration-postgres`, `refacto-stores`). Si ce n'est pas évident depuis le contexte, demande à l'utilisateur :

> « Comment veux-tu nommer ce plan ? (un slug court, ex : `auth-oauth`) »

Le timestamp sur le dossier d'archive garde l'historique si tu refais une confrontation sur le même sujet plus tard.

```bash
SLUG="auth-oauth"  # exemple
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
ARCHIVE_DIR="docs/archives/confront-codex-${SLUG}-${TIMESTAMP}"
mkdir -p "$ARCHIVE_DIR"
```

Mémorise `$ARCHIVE_DIR` et le slug : tous les rounds y sont écrits.

## Le workflow round par round

Les prompts à passer à l'autre sont dans `references/codex-prompts.md`, dans le dossier de ce skill (pas dans le projet). Lis-les avec ton outil de lecture au premier round. Remplace les `{…}` avant de lancer.

### Round 1 : ton plan initial

Rédige ton plan dans `$ARCHIVE_DIR/round-1-<toi>.md`. Le plan doit contenir :

1. **Contexte** — Quel problème on résout, dans quel projet, quelles contraintes
2. **Approche proposée** — Les choix d'architecture, technos, pattern
3. **Étapes d'implémentation** — Découpées clairement
4. **Points sensibles** — Ce que tu identifies comme risqué ou discutable
5. **Alternatives écartées** — Pourquoi tu n'as pas choisi telle ou telle autre voie

Important : écris ce document en sachant qu'il sera challengé. Ne survends pas, ne cache pas les zones d'incertitude. Plus tu es honnête sur les faiblesses, plus le débat sera utile.

### Round 1 : l'avis de l'autre

Lance l'autre avec le prompt « Round 1 », selon « Lancer l'autre et attendre sa réponse ». Sa réponse est enregistrée dans `$ARCHIVE_DIR/round-1-<l'autre>.md`. Ne passe à la suite qu'une fois la commande terminée et ce fichier non vide.

### Round N (N≥2) : ta réponse

Lis le fichier de l'autre du round précédent. Pour chaque point qu'il soulève :

- **S'il a raison** : reconnais-le explicitement, ajuste ton plan, explique ce qui change
- **S'il a tort ou que tu n'es pas d'accord** : explique pourquoi, avec arguments techniques, sans complaisance ni agressivité
- **Si c'est nuancé** : expose la nuance honnêtement, propose éventuellement une voie médiane

Écris ta réponse dans `$ARCHIVE_DIR/round-N-<toi>.md`. Structure recommandée :

```markdown
# Round N — Réponse

## Points où je rejoins l'autre
- [Point X] : il a raison parce que... J'ajuste donc le plan ainsi : ...

## Points où je tiens ma position
- [Point Y] : Je maintiens parce que... Son argument ne tient pas parce que...

## Points où je propose une voie alternative
- [Point Z] : Ni ma version initiale ni la sienne. Je propose plutôt...

## Plan ajusté (état actuel)
[Le plan dans son état actuel, intégrant les ajustements acceptés]
```

### Round N : la réplique de l'autre

Relance l'autre avec le prompt « Round N », en lui listant tous les fichiers précédents dans l'ordre, pour qu'il reste cohérent avec ses propres analyses. Sa réponse va dans `$ARCHIVE_DIR/round-N-<l'autre>.md`.

## Détection du consensus (BILATÉRAL OBLIGATOIRE)

**Règle fondamentale** : tu ne peux JAMAIS déclarer le consensus unilatéralement. Le consensus n'existe que si **l'autre ET toi** l'avez explicitement validé dans un même round. Tant que ce n'est pas le cas, les rounds continuent.

### Le token de consensus

À chaque round à partir du round 2, l'autre doit terminer sa réponse par exactement une de ces deux lignes (les prompts dans `references/codex-prompts.md` l'exigent) :

- `CONSENSUS_ATTEINT` — l'autre confirme qu'aucun désaccord substantiel ne subsiste, le plan est validé en l'état.
- `CONSENSUS_REFUSE` — Au moins un point reste en débat ou un manque subsiste.

Ta première action après lecture du fichier de l'autre est de **chercher ce token en fin de document** (`grep -E '^(CONSENSUS_ATTEINT|CONSENSUS_REFUSE)$' round-N-<l'autre>.md`). Si le token est absent, le round est invalide et tu dois relancer l'autre pour qu'il l'ajoute explicitement.

### Détermination du consensus

**Le consensus est atteint UNIQUEMENT si les deux conditions suivantes sont vraies au même round** :

1. Le fichier de l'autre se termine par `CONSENSUS_ATTEINT`
2. Tu rédiges un fichier `round-N-<toi>-confirm.md` où tu écris explicitement : "Je confirme également le consensus, plus aucun désaccord substantiel de mon côté" — avec ta propre revue du plan finalisé.

Tu peux donc avoir trois cas en lisant le `CONSENSUS_ATTEINT` de l'autre :
- **Tu es d'accord** : rédige ton `round-N-<toi>-confirm.md` confirmant, puis produis le plan final.
- **Tu n'es pas d'accord** (il te reste des objections qu'il n'a pas adressées) : rédige `round-N+1-<toi>.md` listant tes points restants, relance un round. Le consensus n'est PAS atteint.
- **Tu hésites** : remonte à l'utilisateur l'écart de perception avant de continuer.

Symétriquement, si l'autre écrit `CONSENSUS_REFUSE`, tu continues les rounds même si toi tu pensais qu'on avait fini.

### Continue les rounds tant que :
- Au moins l'un des deux camps a un `CONSENSUS_REFUSE` ouvert
- OU l'autre désapprouve un élément du plan
- OU l'autre pointe un manque que tu n'as pas adressé
- OU l'autre propose une amélioration que tu n'as ni acceptée ni explicitement rejetée avec arguments
- OU toi tu identifies un point que l'autre n'a pas suffisamment traité

### Demande à l'utilisateur d'arbitrer si :
- Le débat tourne en rond (3 rounds sans progression réelle sur le ou les mêmes points)
- Vous êtes en désaccord ferme sur un point structurel sans qu'aucun argument ne semble pouvoir convaincre l'un ou l'autre
- **Tu as atteint 5 rounds** : à ce stade, stop systématique. Présente l'état du débat à l'utilisateur et demande comment trancher. Au-delà, le coût (temps, jetons) devient disproportionné par rapport au gain marginal.

Quand tu hésites, formule clairement à l'utilisateur :
- Ce qui reste en débat
- Ta position et celle de l'autre
- Ce que tu recommandes (continuer / arrêter / trancher manuellement)

## Communication avec l'utilisateur entre les rounds

Après chaque round complet (toi + l'autre), donne un bref status :

```
Round N terminé.
- Points sur lesquels nous sommes d'accord : ...
- Points encore en débat : ...
- Mon évaluation : on continue / on arrête / je te laisse trancher

Je lance le round N+1 ?
```

Tu n'es pas obligé de demander à chaque round si l'utilisateur veut continuer — si la progression est claire, enchaîne. Demande explicitement s'il y a une décision à arbitrer ou si tu hésites.

## Production du plan final consolidé

Une fois le consensus bilatéral confirmé (`CONSENSUS_ATTEINT` de l'autre + ta confirmation explicite dans `round-N-<toi>-confirm.md`), écris `docs/plan-{slug}.md` (en utilisant le même slug que pour le dossier d'archive). Ce document doit être :

- **Autonome** : lisible sans connaître l'historique du débat. Quelqu'un qui arrive frais doit pouvoir l'exécuter.
- **Propre** : pas de « l'autre a dit que... », pas de traces du débat. Juste le plan final tel qu'il est maintenant.
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

- `references/codex-prompts.md` — Prompts exacts à passer à l'autre pour chaque round
- `references/exemples.md` — Exemples de bons et mauvais débats pour calibrer ton ton
