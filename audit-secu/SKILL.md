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
- **Aucun identifiant, aucune connexion à un serveur.** Ni Claude, ni les sous-agents, ni Codex
  n'utilisent les accès d'un `.env`, une clé SSH, un compte FTP ou d'administration. Seules les
  pages publiques se lisent, comme un visiteur anonyme. Le bac à sable `read-only` de Codex coupe
  le réseau, mais Codex peut demander une permission, et un relecteur automatique
  (`approvals_reviewer = "auto_review"`) la lui accorde : la commande ci-dessous coupe ces demandes
  (`approval_policy="never"`), et la consigne figure en plus dans chaque prompt.
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

Un dossier sans dépôt git qui en regroupe au moins deux est un **regroupement** : chacun de ses
sous-dossiers devient un projet, nommé `<dossier>/<sous-dossier>` (`PF/PF_SEO`). Dans les noms de
fichiers du rapport (`extraits/`, `tri/`, `codex/`), le `/` devient `__`.

## Étape 0 — Panneau de sélection

Le panneau d'audit (`selection.html`, page claude.ai privée) liste les projets : seuls les circuits
« sous tension » sont scannés. Étape sautée quand des projets sont nommés en argument, et avec
`--reprendre`.

Base de la page : collection `projets`, un document par dossier (`nom`, `scanner`, `raison` parmi
`abandonne`, `mandat`, `autre-dev`, `suspendu` ou `null`, `nouveau`, `veille`), et document `meta/panneau`
(`inventaire` : date ISO, `base`, `dossiers`). Identifiant d'un document : le nom du dossier sans
accents, chaque caractère hors `A-Za-z0-9_.~:@+-` remplacé par `-` (`SPA Lévis` → `SPA-Levis`).

1. Adresse du panneau : clé `page` de `<base>/.audit-secu-projets.json`. Sans elle, publier
   `~/.claude/skills/audit-secu/selection.html` avec
   `capabilities: {"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}, "user": {}}`
   (personne d'autre que le propriétaire ne lit les noms de projets).
2. `python3 ~/.claude/skills/audit-secu/audit.py --lister` donne les dossiers ; lire `projets`
   (ArtifactData `list`, `limit` 1000).
3. Mettre la base à jour par `batch` (50 écritures au plus par appel, chaque document existant
   épinglé par sa `version`) :
   - dossier absent de la base : `set` avec `scanner: true`, `raison: null`, `nouveau: true` ;
   - `nouveau: true` laissé par le passage précédent : `update` à `false` ;
   - document dont le dossier n'existe plus : `delete` ;
   - `meta/panneau` : date et nombre de dossiers du jour.
4. Donner le lien et le relevé (sous tension, hors audit, en veille, nouveaux), puis **attendre le
   feu vert**. Rien n'est scanné avant.
5. Relire `projets` et écrire `<base>/.audit-secu-projets.json` :
   `{"page": "<adresse>", "date": "AAAA-MM-JJ", "exclus": {"<nom>": "<raison ou null>"},
   "veille": ["<nom>"]}`. `veille` : les projets hors audit cochés « Surveiller quand même ». Ils
   sont scannés sans intervention, pour repérer ce qui peut se proposer au client (étape 5).
   Le script lit ce fichier : lancé seul, il respecte la dernière sélection, et le rapport brut
   nomme les projets exclus et ceux en veille.

## Étape 1 — Relevé

```bash
python3 ~/.claude/skills/audit-secu/audit.py [--projet "<nom>" …]
```

La dernière ligne donne le dossier du rapport. Lire `rapport-brut.md` pour la vue d'ensemble,
`brut.json` pour le détail. Avec `--brut` : résumer la vue d'ensemble et s'arrêter.

Le script prépare aussi le tri : `a-trier.json` (projets des lots `complet`, `dev_seulement` et
`veille`), `extraits/<projet>.json` (failles moyennes ou plus, composants WordPress élevés ou
plus ; pour un projet en veille, seulement les failles élevées ou critiques hors développement) et
`extraits/_modeles.json` (occurrences de modèles d'IA). Les sous-agents lisent
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
**hors développement**, ou une extension WordPress de gravité élevée ou plus. Le lot `veille` ne
passe ni au tri ni à Codex : il va directement à l'étape 5.

- **Un sous-agent Opus par projet**, lancés en parallèle (par vagues de 8 au plus).
- **Un seul sous-agent Sonnet pour le lot « développement seulement »** : les projets dont toutes
  les failles sont marquées dev. Il vérifie que ces paquets ne servent qu'à construire ou tester
  (et ne finissent pas dans ce qui est déployé). Si l'un d'eux s'avère utilisé en production, le
  projet passe au tri complet.

Prompt du sous-agent projet (adapter les données, garder les consignes) :

```
Tri de failles connues dans <chemin du projet>, en LECTURE SEULE : ne modifie rien, n'installe
rien, ne lance ni build ni tests. N'utilise aucun identifiant (.env, clé SSH, FTP, compte) et ne
te connecte à aucun serveur : seules les pages publiques peuvent être lues, en visiteur anonyme.
Le relevé ci-dessous vient d'un script : il peut se tromper (version, portée dev/prod). Ne me
fais pas confiance, vérifie dans les fichiers.

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
  -c approval_policy="never" \
  --sandbox read-only \
  --skip-git-repo-check \
  -C "<chemin du projet>" \
  -o "<rapport>/codex/<projet>.md" \
  "PROMPT" > "<rapport>/codex/<projet>.log" 2>&1 < /dev/null
```

Le PROMPT donne les failles et les verdicts de Claude, et demande pour chacune `CONFIRME` ou
`CONTESTE`, avec la raison et les preuves en fichier:ligne, sans se fier à l'analyse de Claude.
Il reprend mot pour mot l'interdiction des identifiants et des connexions aux serveurs (voir
Règles) : sans elle et sans `approval_policy="never"`, Codex lit le `.env` et se connecte à la
production par FTP ou SSH pour vérifier une version.
Modèle refusé : citer l'erreur telle quelle, ne pas basculer seul vers un autre modèle.

Un désaccord ne se tranche pas en silence : les deux avis figurent dans le rapport.

## Étape 5 — Occasions (projets en veille)

Les projets du lot `veille` sont hors mandat : pas de tri, pas de Codex, pas de correctif. Le but
est de repérer ce qui peut se proposer au client. Un seul sous-agent Sonnet pour tout le lot, avec
les interdits du tri (lecture seule, aucun identifiant, aucune connexion à un serveur, pages
publiques en visiteur anonyme). Pour chaque paquet ou composant de `extraits/<projet>.json` :

1. Adresse du site : CLAUDE.md, README ou configuration du projet. Sans adresse : « copie locale
   seulement ».
2. Version servie en production, lue par une requête publique : `?ver=` des scripts et styles
   d'une extension WordPress, son `readme.txt` public, empreinte du script Livewire… Requêtes
   `GET` seulement, sans formulaire ni connexion.
3. Statut : *constaté en production* (la version servie est vulnérable), *corrigé en production*
   (la copie locale est en retard, rien à proposer), *copie locale seulement* (version en ligne
   illisible ou site introuvable).
4. Le problème en une phrase qu'un client comprend, et l'offre possible (mise à jour, contrat de
   maintenance…).

Les appels réels à un modèle d'IA retiré ou déprécié (étape 2) dans ces projets sont aussi des
occasions.

## Étape 6 — Rapport final

`<rapport>/rapport.md`, en français clair, dans cet ordre :

1. **En-tête** : date, projets couverts (dont ceux en veille), ce qui n'est pas couvert
   (production ; failles du code maison), fraîcheur de la table des modèles.
2. **🔴 À corriger maintenant** : projet, paquet, faille en une phrase, pourquoi (Claude), avis de
   Codex, correctif, risque de casse.
3. **🟠 À planifier**, puis **🟡 À surveiller** (une ligne par paquet).
4. **WordPress, copies locales** : extensions en faille élevée ou critique, avec la version
   corrigée. Rappeler que la version en production se lit dans le monitoring, pas ici.
5. **Fins de support et retards de version majeure.**
6. **Modèles d'IA** : appels réels à remplacer, renvoi vers `/maj-modeles`.
7. **Désaccords Claude / Codex.**
8. **💡 Occasions (projets en veille)** : projet, problème en une phrase, statut, offre possible.
   Ceux déjà corrigés en production n'y figurent pas. Rien ne part vers un client sans la
   validation de l'utilisateur et un passage par `/humanize`.
9. **Angles morts** : projets sans GitHub, Dependabot coupé, fichiers non analysables.

## Étape 7 — Message à l'utilisateur

Court : les urgences en tête (cinq au plus), le nombre d'occasions, le chemin complet du rapport,
les statuts explicites (relevé constaté, verdicts jugés sans exécution, production non couverte).
Proposer ensuite : corriger un projet (session à part, avec son accord), `/maj-modeles` pour les
modèles.
