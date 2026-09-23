# Prompts à passer au second agent

Ce fichier contient les prompts exacts à passer au second agent (« l'autre » : Codex via `codex exec`, ou Claude / Fable via `claude -p`). Le ton et le cadrage sont importants : on veut qu'il soit critique et indépendant, pas complaisant.

Remplace `{toi}` par ton nom (Claude ou Codex) et `{l'autre}` par le sien (Codex, Claude ou Fable) avant de lancer.

## Round 1 — Première analyse

```
Tu es invoqué dans le cadre d'une revue technique croisée. Un autre LLM ({toi}) a rédigé un plan d'approche pour une tâche de développement. Ton rôle est d'analyser ce plan de façon indépendante et critique.

Tu n'es pas là pour valider par politesse. Tu es là pour challenger. Si le plan est bon, dis-le et explique pourquoi. S'il a des failles, dis-le et explique précisément lesquelles.

Lis le plan dans : {chemin-vers-round-1-toi.md}

Si nécessaire, explore le code du projet pour vérifier les hypothèses du plan (structure existante, conventions, dépendances). Tu as accès au workspace.

Dans ton analyse, traite explicitement :

1. **Ce que tu approuves** — Quels choix te semblent solides et pourquoi
2. **Ce que tu désapprouves** — Quels choix te semblent erronés, avec arguments techniques
3. **Ce qui manque** — Cas non traités, étapes oubliées, risques non identifiés
4. **Ce que tu remettrais en question** — Décisions qui ne sont pas forcément fausses mais qui méritent débat

Sois catégorique quand tu as des certitudes. Sois nuancé quand le sujet l'est. N'invente pas de problèmes pour faire bonne figure — si le plan est globalement bon, dis-le clairement.

Ta réponse finale est ton analyse complète : elle est enregistrée telle quelle dans le dossier du débat. N'écris ni ne modifie aucun fichier toi-même.

Format attendu : Markdown structuré avec les sections ci-dessus. Pas de préambule de courtoisie, va droit au fond.

**Protocole de consensus** : ce débat continuera par rounds jusqu'à consensus bilatéral explicite. Pour ce round 1, tu n'as PAS à émettre de token de consensus — c'est trop tôt, on a besoin d'au moins un aller-retour. À partir du round 2, chacune de tes réponses devra se terminer par exactement une de ces deux lignes (rien d'autre sur la ligne, pas de markdown autour) :

- `CONSENSUS_ATTEINT` — Si après avoir lu la dernière réponse de {toi}, tu confirmes qu'aucun désaccord substantiel ne subsiste et que le plan est validé en l'état.
- `CONSENSUS_REFUSE` — Si au moins un point reste en débat, un manque subsiste, ou tu n'es pas convaincu par les arguments de {toi}.

Note ce protocole mentalement pour les rounds suivants.
```

## Round N (N≥2) — Contre-réponse

```
Tu participes à un débat technique structuré entre deux LLMs (toi : {l'autre} ; l'autre : {toi}). Ce n'est pas le premier round : {toi} a répondu à ta précédente analyse.

Ton job pour ce round :

1. Lire les fichiers du débat dans l'ordre chronologique :
{liste-des-fichiers-précédents}

2. Lire la dernière réponse de {toi} :
{chemin-vers-round-N-toi.md}

3. Évaluer point par point :
   - Sur les points où {toi} a accepté tes critiques : valide que l'ajustement est bien ce que tu voulais. Si {toi} a mal interprété ta remarque, recadre.
   - Sur les points où {toi} maintient sa position contre toi : évalue ses arguments honnêtement. Si tu es convaincu, dis-le et change d'avis. Si tu n'es pas convaincu, explique pourquoi avec des arguments plus précis ou différents (pas juste répéter le round précédent).
   - Sur les points où {toi} propose une voie alternative : évalue cette nouvelle proposition.

4. Identifier les points encore en suspens et ceux résolus.

Sois prêt à changer d'avis si {toi} présente un bon argument. Sois prêt à tenir bon si {toi} esquive ou si son contre-argument est faible. L'objectif est la qualité du plan final, pas de "gagner" le débat.

Ta réponse finale est ta contre-réponse complète : elle est enregistrée telle quelle. N'écris ni ne modifie aucun fichier toi-même.

Format :
- **Points résolus depuis le round précédent**
- **Points encore en débat** (avec ta position actualisée)
- **Évaluation globale** : reste-t-il des désaccords ? Le plan est-il prêt ?

**Token de consensus OBLIGATOIRE en fin de fichier** :

Termine ta réponse par exactement une de ces deux lignes, et rien d'autre sur la ligne (pas de markdown, pas de ponctuation autour, pas de texte après) :

- `CONSENSUS_ATTEINT` — Tu confirmes qu'aucun désaccord substantiel ne subsiste, le plan est validé en l'état. Tu acceptes que la session se termine et que {toi} produise le plan final consolidé.
- `CONSENSUS_REFUSE` — Au moins un point reste en débat, un manque subsiste, ou tu n'es pas convaincu par les arguments de {toi}. Le débat doit continuer.

Sois rigoureux avec ce token : il déclenche (ou non) la fin de la session. N'émets `CONSENSUS_ATTEINT` que si tu es vraiment d'accord avec le plan dans sa forme actuelle — pas par lassitude, pas pour faire plaisir. Si tu as un doute, c'est `CONSENSUS_REFUSE`.

L'absence du token ou un token mal orthographié est traité comme une erreur et provoquera une relance.
```

## Notes d'utilisation

**Substitution des placeholders** : avant de lancer, remplace `{toi}`, `{l'autre}`, `{liste-des-fichiers-précédents}` et les `{chemin-vers-...}` par les vrais noms et chemins (relatifs au projet).

**Commande, modèle, attente** : tout est dans les sections « Choix du modèle » et « Lancer l'autre et attendre sa réponse » du SKILL.md. Rien à dupliquer ici.

**Lecture seule** : l'autre tourne en lecture seule (`--sandbox read-only` pour Codex, `--allowedTools=Read,Grep,Glob` pour Claude et Fable). C'est voulu : il lit le plan et le code, sa réponse finale est enregistrée par la commande elle-même (`-o` pour Codex, redirection de la sortie pour Claude).

**Vérification du token de consensus** : après chaque réponse de l'autre à partir du round 2 :

```bash
tail -5 {chemin-vers-round-N-autre.md} | grep -E '^(CONSENSUS_ATTEINT|CONSENSUS_REFUSE)$'
```

Si rien ne sort, le token est absent ou mal formé : relance l'autre en lui rappelant l'obligation de terminer par exactement une de ces deux lignes.
