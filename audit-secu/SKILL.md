---
name: audit-secu
description: "Passe tous les projets d'un dossier de travail au crible des failles connues (npm, pnpm, composer, Python, extensions WordPress, alertes GitHub Dependabot), des technologies en fin de support et des modèles d'IA périmés, puis trie chaque faille avec des sous-agents et un second avis Codex. Rapport seulement, rien n'est modifié. Trigger /audit-secu, « audit de sécurité », « scanne mes projets », « vérifie les failles », « dépendances vulnérables », « quoi mettre à jour »."
---

# Audit de sécurité multi-projets

Un script sans IA fait le relevé (gratuit, environ une minute pour 80 projets), puis Claude trie
ce qui mérite de l'être et Codex donne un second avis sur les cas graves ou douteux.

## Règles

- **Lecture seule.** Rien n'est modifié, installé ni commité dans les projets. Les correctifs se
  font ensuite, projet par projet, sur accord explicite.
- **Rapports confidentiels.** Ils listent des failles de sites clients : ils restent dans
  `<base>/.audit-secu-rapports/AAAA-MM-JJ/`, jamais dans un commit, jamais tels quels dans un
  message à un client.
- **Trois statuts, jamais confondus dans le rapport :**
  - *constaté par l'outil* : sortie du script (npm, composer, GitHub, bases publiques) ;
  - *jugement* : conclusion d'un sous-agent ou de Codex, tirée de la lecture du code, sans
    exécution ;
  - *non couvert* : la production. Une copie locale peut différer du site en ligne, et les
    alertes GitHub portent sur la branche poussée.

## Arguments

- `/audit-secu` : tous les projets du dossier (défaut `~/Apps-coding`, sauf `ZZ-POUBELLE`).
- `/audit-secu <projet> [<projet>…]` : seulement ceux-là (nom du dossier de premier niveau).
- `--brut` : relevé seul, sans tri ni Codex.
- `--reprendre` : réutiliser le `brut.json` du jour s'il existe, au lieu de relancer le script.

Chemins à ignorer (copies, preuves…) : un par ligne dans `<base>/.audit-secu-ignorer`.

## Étape 1 — Relevé

```bash
python3 ~/.claude/skills/audit-secu/audit.py [--projet "<nom>" …]
```

La dernière ligne donne le dossier du rapport. Lire `rapport-brut.md` pour la vue d'ensemble,
`brut.json` pour le détail. Avec `--brut` : résumer la vue d'ensemble et s'arrêter.

Le script prépare aussi le tri : `a-trier.json` (projets du lot `complet` et du lot
`dev_seulement`), `extraits/<projet>.json` (failles moyennes ou plus, composants WordPress
élevés ou plus) et `extraits/_modeles.json` (occurrences de modèles d'IA). Les sous-agents lisent
ces fichiers eux-mêmes : ne pas recopier leur contenu dans les prompts.

npm, pnpm et composer tournent sur une copie temporaire des seuls fichiers de dépendances, sans
les jetons de l'environnement : aucune config ni aucun crochet du projet n'est chargé.

Ce que le script couvre, et ce qu'il écarte exprès :
- npm (`npm audit --package-lock-only`), pnpm, composer (`audit`, `outdated --major-only`, paquets
  abandonnés), `requirements.txt` figés (OSV) ; chaque faille dit si elle ne touche que les
  dépendances de développement (`devDependencies`, `require-dev`). Ça ne veut pas dire « non
  déployé » : un paquet compilé dans le JavaScript du site (axios dans Laravel, par exemple) part
  en production ;
- extensions et thèmes WordPress par leur version (WPVulnerability, données CC0) ; les fichiers de
  dépendances internes aux extensions tierces sont écartés, ainsi que les alertes GitHub qui les
  visent ;
- alertes GitHub : Dependabot, analyse de code et secrets quand c'est activé ;
- fins de support (endoflife.date) : WordPress, Laravel, Symfony, React, Vue, Next, Nuxt, Angular,
  Express, jQuery, Tailwind, Node (`.nvmrc`), PHP (seulement si `config.platform.php`) ;
- modèles d'IA comparés à la table de `/maj-modeles` (`ancien selon la table` ou `hors table`).

## Étape 2 — Modèles d'IA

1. **Fraîcheur de la table.** Comparer `~/.claude/skills/maj-modeles/model-map.json` au tableau
   des modèles actuels du skill `claude-api`. Un modèle plus récent absent de la table : l'écrire
   en tête du rapport (« table périmée, X existe »).
2. **Contexte de chaque occurrence.** Un sous-agent Haiku lit la ligne de chaque occurrence et la
   classe : *appel réel* (identifiant envoyé à une API), *test de préfixe* (`str_starts_with`,
   `startsWith`…), *migration historique*, *test*, *liste ou tarifs*. Seuls les appels réels sont
   « à remplacer ». Les `hors table` Anthropic se jugent avec le skill `claude-api` (retiré,
   déprécié, alias) ; OpenAI et Gemini restent « à vérifier » sans doc officielle lue.
3. La correction relève de `/maj-modeles`, lancé dans le projet concerné : ne pas la faire ici.

## Étape 3 — Tri par sous-agents

Projets à trier (`a-trier.json`, lot `complet`) : au moins une faille de gravité moyenne ou plus
**hors développement**, ou une extension WordPress de gravité élevée ou plus.

- **Un sous-agent Opus par projet**, lancés en parallèle (par vagues de 8 au plus).
- **Un seul sous-agent Sonnet pour le lot « développement seulement »** : les projets dont toutes
  les failles sont marquées dev. Il vérifie que ces paquets ne servent qu'à construire ou tester
  (et ne finissent pas dans ce qui est déployé). Si l'un d'eux s'avère utilisé en production, le
  projet passe au tri complet.

Prompt du sous-agent projet (adapter les données, garder les consignes) :

```
Tri de failles connues dans <chemin du projet>, en LECTURE SEULE : ne modifie rien, n'installe
rien, ne lance ni build ni tests. Le relevé ci-dessous vient d'un script : il peut se tromper
(version, portée dev/prod). Ne me fais pas confiance, vérifie dans les fichiers.

Contexte du projet : lis d'abord son CLAUDE.md ou son README (public ou interne ? en ligne ?).

Relevé : lis <rapport>/extraits/<projet>.json (failles ≥ moyenne, composants WordPress ≥ élevée).

Regroupe par paquet (plusieurs avis sur un même paquet = un seul verdict). Pour chaque paquet :
1. Portée : dépendance de production, ou outil de build / test seulement ? Preuve : fichier:ligne.
2. Atteignabilité : le code du projet utilise-t-il la fonction ou le module vulnérable ? Cite
   fichier:ligne, ou la recherche faite sans résultat. Pour WordPress : la faille demande-t-elle
   un compte (vecteur CVSS, PR:N ou non) ? la fonction vulnérable est-elle utilisée sur le site ?
3. Exposition : qui peut atteindre ce code (public, connecté, administrateur, local) ?
4. Verdict : maintenant | planifier | surveiller | incertain.
5. Correctif : commande ou version cible, saut de version majeure ou non, risque de casse.

Réponds par un bloc ```json : [{"paquet", "ids", "verdict", "raison" (1 à 2 phrases en français),
"preuves": ["fichier:ligne"], "correctif", "risque_casse"}].
```

## Étape 4 — Second avis Codex

Pour chaque projet trié, soumettre à Codex les verdicts `maintenant` et `incertain`, ainsi que
toute faille **critique** que Claude a classée `planifier` ou `surveiller` (le doute joue dans les
deux sens). Un seul appel par projet, plusieurs projets en parallèle (4 au plus) :

```bash
timeout 30m codex exec \
  --model gpt-6-astra \
  -c model_reasoning_effort="high" \
  --sandbox read-only \
  --skip-git-repo-check \
  -C "<chemin du projet>" \
  -o "<rapport>/codex/<projet>.md" \
  "PROMPT" > "<rapport>/codex/<projet>.log" 2>&1 < /dev/null
```

Le PROMPT donne les failles et les verdicts de Claude, et demande pour chacune `CONFIRME` ou
`CONTESTE`, avec la raison et les preuves en fichier:ligne, sans se fier à l'analyse de Claude.
Modèle refusé : citer l'erreur telle quelle, ne pas basculer seul vers un autre modèle.

Un désaccord ne se tranche pas en silence : les deux avis figurent dans le rapport.

## Étape 5 — Rapport final

`<rapport>/rapport.md`, en français clair, dans cet ordre :

1. **En-tête** : date, projets couverts, ce qui n'est pas couvert (production ; failles du code
   maison), fraîcheur de la table des modèles.
2. **🔴 À corriger maintenant** : projet, paquet, faille en une phrase, pourquoi (Claude), avis de
   Codex, correctif, risque de casse.
3. **🟠 À planifier**, puis **🟡 À surveiller** (une ligne par paquet).
4. **WordPress, copies locales** : extensions en faille élevée ou critique, avec la version
   corrigée. Rappeler que la version en production se lit dans le monitoring, pas ici.
5. **Fins de support et retards de version majeure.**
6. **Modèles d'IA** : appels réels à remplacer, renvoi vers `/maj-modeles`.
7. **Désaccords Claude / Codex.**
8. **Angles morts** : projets sans GitHub, Dependabot coupé, fichiers non analysables.

## Étape 6 — Message à l'utilisateur

Court : les urgences en tête (cinq au plus), le chemin complet du rapport, les statuts explicites
(relevé constaté, verdicts jugés sans exécution, production non couverte). Proposer ensuite :
corriger un projet (session à part, avec son accord), `/maj-modeles` pour les modèles.
