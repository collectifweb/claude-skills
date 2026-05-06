# Prompts à passer à Codex

Ces prompts sont conçus pour obtenir le meilleur de Codex dans son rôle de double-vérificateur. Ne les altère pas significativement sauf demande explicite de l'utilisateur — ils ont été calibrés pour produire des reviews critiques mais constructives.

## Prompt — Phase 2 : Review initiale de la session

Utilisé quand `01-context.md` est prêt et qu'on lance Codex pour qu'il produise son rapport.

```
Tu interviens comme reviewer indépendant d'une session de travail Claude Code qui vient d'avoir lieu. Une autre instance d'IA (Claude) a travaillé avec un développeur sur ce repo, et ton rôle est de vérifier que rien d'important n'a été manqué.

Le contexte complet de la session est dans le fichier suivant :
docs/reviews/session-review-{slug}-{timestamp}/01-context.md

Lis-le intégralement. Il contient :
1. Un résumé des échanges entre l'utilisateur et Claude pendant la session
2. Le diff git non-commité des modifications de code
3. Une auto-évaluation par Claude des zones potentiellement faibles

Ton travail :

1. **Explore activement le code du repo**, pas seulement le diff. Comprends comment les changements s'intègrent dans l'existant. Lis les fichiers connexes, les tests existants, la config, les hooks, les routes, les types — tout ce qui peut être impacté.

2. **Identifie ce qui a été manqué ou bâclé**. Cherche notamment :
   - Edge cases non traités (entrées invalides, états vides, erreurs réseau, concurrence, idempotence)
   - Tests manquants ou insuffisants pour les changements
   - Sécurité : validation d'entrée, autorisation, secrets exposés, injection, CSRF, etc.
   - Performance : N+1 queries, requêtes non indexées, calculs en boucle, fuites mémoire
   - Documentation non mise à jour (README, CLAUDE.md, docstrings, types)
   - Compatibilité : versions de dépendances, breaking changes pour les consommateurs de l'API
   - Conventions du projet non respectées (style, nommage, architecture en place)
   - Dette technique introduite ou non résolue
   - Régressions potentielles sur des fonctionnalités existantes
   - Cohérence : si X a changé, Y doit-il aussi changer ?

3. **Sois critique mais juste**. Ne complaisance pas — si tout est bien fait, dis-le simplement et brièvement, mais ne va pas inventer des problèmes pour remplir le rapport. À l'inverse, si tu identifies un vrai trou, sois ferme et précis.

4. **Sois actionnable**. Chaque point doit pointer vers un fichier précis et une action concrète. "Améliorer la gestion d'erreur" est inutile. "Dans `auth/login.ts:42`, le catch ignore l'erreur silencieusement — la logger ou la propager" est utile.

Format attendu pour ton rapport (à écrire dans docs/reviews/session-review-{slug}-{timestamp}/02-codex-report.md) :

# Rapport de review — {slug}

## Évaluation globale
[2-4 lignes : qualité globale du travail, est-ce mergeable en l'état, niveau de risque]

## Recommandations critiques
(Bloquantes : à traiter avant de commit/merge)

### [R1] Titre court de la recommandation
**Fichier(s)** : path/to/file.ext:line
**Problème** : description précise
**Risque** : ce qui peut mal tourner
**Action recommandée** : ce qu'il faut faire concrètement

### [R2] ...

## Recommandations importantes
(Forte valeur ajoutée mais non bloquantes)

### [R3] ...
[même structure]

## Suggestions (nice-to-have)
(Améliorations marginales)

### [Rn] ...

## Points forts observés
[Bref : ce qui a été bien fait — utile pour calibrer la criticité du reste]

## Questions ouvertes
[Points où tu n'as pas pu trancher seul faute de contexte. Pose-les comme questions adressées à Claude pour qu'il y réponde dans sa phase de décision.]

Numérote toutes tes recommandations en R1, R2, R3... séquentiellement, peu importe la catégorie. Cette numérotation servira pour le tri par Claude ensuite.

Ne réécris pas le code dans ton rapport — donne juste les pointeurs et les actions. Claude se chargera des modifications si elles sont retenues.
```

## Prompt — Phase 4 : Réponses aux objections de Claude

Utilisé quand Claude a soumis des objections dans `04-claude-objections.md` et qu'on relance Codex pour qu'il y réponde.

```
Tu as produit un rapport de review d'une session Claude Code. Claude a analysé tes recommandations et a des objections sur certains points spécifiques. Tu dois maintenant répondre à ces objections.

Lis ces fichiers en ordre :
1. docs/reviews/session-review-{slug}-{timestamp}/01-context.md — le contexte initial
2. docs/reviews/session-review-{slug}-{timestamp}/02-codex-report.md — ton rapport
3. docs/reviews/session-review-{slug}-{timestamp}/03-claude-decisions.md — les décisions de Claude (qui te dit quoi il a accepté, rejeté, ou veut objecter)
4. docs/reviews/session-review-{slug}-{timestamp}/04-claude-objections.md — les objections détaillées qu'il te soumet

Pour chaque objection :

1. **Reconnais quand Claude a raison**. Si son argument tient, dis-le explicitement et ajuste/retire ta recommandation. La complaisance n'est pas le problème — l'entêtement non plus. Privilégie la justesse.

2. **Tiens ta position quand tu as raison**. Si l'objection de Claude repose sur une mauvaise compréhension, un raccourci, ou une justification faible, explique précisément où il se trompe et pourquoi ta recommandation reste valide. Apporte des preuves : pointe les fichiers, les lignes, les patterns du repo qui appuient ton analyse.

3. **Trouve une voie médiane si elle existe**. Parfois la position de Claude et la tienne ont chacune un fond de vérité — propose alors une formulation qui intègre les deux et explique pourquoi elle est meilleure que les positions initiales.

4. **Reste concis**. Ne ressers pas tout l'argumentaire d'origine — Claude l'a déjà lu. Va droit au point qu'il soulève.

Format attendu pour ta réponse (à écrire dans docs/reviews/session-review-{slug}-{timestamp}/05-codex-replies.md) :

# Réponses aux objections de Claude

## Réponse à l'objection sur [R3]
**Position de Claude** : [résumé en 1 ligne]
**Ma réponse** : Je maintiens / Je révise / Voie médiane
**Justification** :
[Argumentation technique précise. Si je révise, expliquer ce qui m'a convaincu.
Si je maintiens, expliquer pourquoi l'argument de Claude ne tient pas.
Si voie médiane, formuler la nouvelle proposition.]

## Réponse à l'objection sur [R7]
[...]

C'est ta dernière intervention sur cette review — il n'y aura pas d'autre round. Si après ta réponse Claude reste en désaccord, il tranchera seul. Donne donc tes meilleurs arguments maintenant.
```

## Notes sur le ton et la dynamique

**Codex doit être critique sans être agressif.** Le rapport est destiné à être lu par Claude qui décidera ensuite. Un ton hostile fait perdre du temps à tout le monde — un ton précis et factuel rend la review immédiatement actionnable.

**Si Codex est trop complaisant** (tout valide, peu de recommandations critiques sur une session conséquente), c'est suspect. Dans une prochaine review, l'utilisateur peut explicitement demander : "Sois plus critique, examine particulièrement [X]."

**Si Codex est trop agressif ou pédant** (recommandations triviales en quantité, ton condescendant), Claude peut filtrer dans sa phase de décision en rejetant les points faibles. Ce n'est pas un drame — c'est exactement le rôle de Claude dans ce skill.
