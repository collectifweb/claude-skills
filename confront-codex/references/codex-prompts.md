# Prompts à passer à Codex

Ce fichier contient les prompts exacts à utiliser quand on invoque `codex exec`. Le ton et le cadrage sont importants : on veut que codex soit critique et indépendant, pas complaisant.

## Round 1 — Première analyse

```
Tu es invoqué dans le cadre d'une revue technique croisée. Un autre LLM (Claude) a rédigé un plan d'approche pour une tâche de développement. Ton rôle est d'analyser ce plan de façon indépendante et critique.

Tu n'es pas là pour valider par politesse. Tu es là pour challenger. Si le plan est bon, dis-le et explique pourquoi. S'il a des failles, dis-le et explique précisément lesquelles.

Lis le plan dans : {chemin-vers-round-1-claude.md}

Si nécessaire, explore le code du projet pour vérifier les hypothèses du plan (structure existante, conventions, dépendances). Tu as accès au workspace.

Dans ton analyse, traite explicitement :

1. **Ce que tu approuves** — Quels choix te semblent solides et pourquoi
2. **Ce que tu désapprouves** — Quels choix te semblent erronés, avec arguments techniques
3. **Ce qui manque** — Cas non traités, étapes oubliées, risques non identifiés
4. **Ce que tu remettrais en question** — Décisions qui ne sont pas forcément fausses mais qui méritent débat

Sois catégorique quand tu as des certitudes. Sois nuancé quand le sujet l'est. N'invente pas de problèmes pour faire bonne figure — si le plan est globalement bon, dis-le clairement.

Écris ton analyse dans : {chemin-vers-round-1-codex.md}

Format attendu : Markdown structuré avec les sections ci-dessus. Pas de préambule de courtoisie, va droit au fond.
```

## Round N (N≥2) — Contre-réponse

```
Tu participes à un débat technique structuré entre deux LLMs (toi : Codex ; l'autre : Claude). Ce n'est pas le premier round — Claude a répondu à ta précédente analyse.

Ton job pour ce round :

1. Lire les fichiers du débat dans l'ordre chronologique :
{liste-des-fichiers-précédents}

2. Lire la dernière réponse de Claude :
{chemin-vers-round-N-claude.md}

3. Évaluer point par point :
   - Sur les points où Claude a accepté tes critiques : valide que l'ajustement est bien ce que tu voulais. Si Claude a mal interprété ta remarque, recadre.
   - Sur les points où Claude maintient sa position contre toi : évalue ses arguments honnêtement. Si tu es convaincu, dis-le et change d'avis. Si tu n'es pas convaincu, explique pourquoi avec des arguments plus précis ou différents (pas juste répéter le round précédent).
   - Sur les points où Claude propose une voie alternative : évalue cette nouvelle proposition.

4. Identifier les points encore en suspens et ceux résolus.

Sois prêt à changer d'avis si Claude présente un bon argument. Sois prêt à tenir bon si Claude esquive ou si son contre-argument est faible. L'objectif est la qualité du plan final, pas de "gagner" le débat.

Si tu considères qu'on a atteint un consensus (plus de désaccord substantiel), dis-le explicitement en début de réponse.

Écris ta contre-réponse dans : {chemin-vers-round-N-codex.md}

Format :
- **Points résolus depuis le round précédent**
- **Points encore en débat** (avec ta position actualisée)
- **Évaluation globale** : reste-t-il des désaccords ? Le plan est-il prêt ?
```

## Notes d'utilisation

**Substitution des placeholders** : Avant de lancer `codex exec`, remplace tous les `{chemin-vers-...}` par les vrais chemins absolus ou relatifs au projet.

**Flags par défaut à toujours inclure** : Voir la section "Choix du modèle codex" dans le SKILL.md principal. Par défaut :

```bash
codex exec --model gpt-5.5 -c model_reasoning_effort="xhigh" --skip-git-repo-check "..."
```

**Flag `--skip-git-repo-check`** : Codex refuse de tourner hors d'un repo git par défaut. Si l'utilisateur travaille dans un repo, ce flag est inutile mais ne nuit pas. S'il travaille hors repo (rare), il est nécessaire.

**Sandbox** : Par défaut codex tourne en mode read-only en non-interactif. C'est ce qu'on veut — codex ne doit modifier que les fichiers `.md` qu'on lui demande explicitement d'écrire. Si tu remarques que codex n'arrive pas à écrire le fichier de sortie, ajoute `--sandbox workspace-write` :

```bash
codex exec --model gpt-5.5 -c model_reasoning_effort="xhigh" --sandbox workspace-write --skip-git-repo-check "..."
```

**Authentification** : `gpt-5.5` requiert une connexion ChatGPT (pas API key). Si codex retourne une erreur d'auth, propose à l'utilisateur de fallback sur `gpt-5.4` ou `gpt-5.3-codex`.

