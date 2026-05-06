---
name: confront-codex
description: Confronte un plan d'approche technique de Claude avec une analyse indépendante de Codex (CLI), via plusieurs rounds de débat documentés, jusqu'à atteindre un consensus. Utilise ce skill dès que l'utilisateur demande de "confronter codex", "valider le plan avec codex", "lancer une review codex", "challenger l'approche", "second avis sur le plan", ou tape la slash command `/confront-codex`. Utilise-le aussi proactivement quand l'utilisateur termine un plan en plan mode et qu'il a déjà mentionné dans la conversation vouloir une validation croisée avec codex. Le skill produit un plan final consolidé dans `docs/` après débat itératif, avec archivage des rounds intermédiaires dans `docs/archives/`.
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

**Concrètement** : toutes les invocations de `codex exec` dans ce skill doivent inclure ces flags par défaut :

```bash
codex exec \
  --model gpt-5.5 \
  -c model_reasoning_effort="xhigh" \
  --skip-git-repo-check \
  "PROMPT_ICI"
```

Si l'utilisateur demande un modèle différent, remplace `gpt-5.5` par le modèle demandé. Si l'utilisateur dit explicitement "sans xhigh" ou "reasoning normal", retire le flag `-c model_reasoning_effort="xhigh"`.

**Note sur `gpt-5.5`** : ce modèle requiert une authentification ChatGPT (pas API key). Si tu obtiens une erreur d'authentification, signale-le à l'utilisateur et propose de basculer sur `gpt-5.4` ou `gpt-5.3-codex` comme fallback.

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

Lance codex en mode non-interactif (avec les flags du modèle, voir section "Choix du modèle codex" plus haut) :

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
)"
```

Codex va lire ton plan, écrire son analyse, et terminer. Cette opération peut prendre plusieurs minutes — c'est normal, codex explore le code et raisonne. Ne t'inquiète pas du temps d'attente. Vérifie ensuite que le fichier `round-1-codex.md` a bien été créé.

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

Relance codex avec le prompt de round suivant (voir `references/codex-prompts.md`). Codex doit lire le dernier fichier de toi et ses propres analyses précédentes pour rester cohérent.

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
)"
```

## Détection du consensus

Après chaque round de Codex, lis attentivement son fichier et évalue : reste-t-il des désaccords substantiels ?

**Continue les rounds tant que :**
- Codex désapprouve un élément du plan
- Codex pointe un manque que tu n'as pas adressé
- Codex propose une amélioration que tu n'as ni acceptée ni explicitement rejetée avec arguments

**Le consensus est atteint quand :**
- Codex valide explicitement le plan dans son ensemble
- OU les seuls points restants sont des préférences stylistiques mineures que les deux camps reconnaissent comme telles
- OU Codex et toi avez convergé vers une formulation que vous reconnaissez tous deux comme satisfaisante

**Demande à l'utilisateur d'arbitrer si :**
- Le débat tourne en rond (3 rounds sans progression réelle)
- Codex et toi êtes en désaccord ferme sur un point structurel sans qu'aucun argument ne semble pouvoir convaincre l'autre
- Tu as un doute sur la pertinence de continuer
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

Une fois le consensus atteint, écris `docs/plan-{slug}.md` (en utilisant le même slug que pour le dossier d'archive). Ce document doit être :

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
