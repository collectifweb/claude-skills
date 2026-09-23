---
name: timelog
description: "Génère la synthèse d'une journée pour Toggl, en blocs horaires tirés des commits git et des sessions Claude Code et Codex (seuil 90 min). Variante /timelog quick, survol multi-jours multi-projets sans détail horaire, pour répondre à « sur quels projets j'ai travaillé ». Trigger /timelog, /timelog quick, \"log de temps\", \"synthèse journée\", \"résume ce que j'ai fait\", \"time tracking\", \"quels projets cette semaine\", \"sur quels projets j'ai travaillé\"."
---

# Timelog

Génère des entrées de log de temps en français pour le projet client courant, à partir de l'activité git, des sessions Claude Code **et des sessions Codex CLI** de la journée.

Fonctionne de la même façon dans Claude Code et dans Codex CLI : les deux types de sessions sont fusionnés dans la même chronologie, quel que soit l'agent qui lance le skill.

## Quand l'utiliser

L'utilisateur travaille comme dev freelance et logue son temps dans Toggl à la fin de la journée (ou plus tard). Il déclenche ce skill depuis le dossier d'un projet client pour obtenir une synthèse compréhensible par des clients non-techniques mais qui montre quand même la maîtrise technique.

Ce skill est lancé **uniquement** depuis un dossier de projet client. Le `cwd` au moment de l'exécution détermine quel projet analyser, point.

## Paramètres

L'utilisateur peut spécifier :
- **Une date** : "aujourd'hui" (défaut), "hier", ou une date au format `YYYY-MM-DD` ou `JJ/MM`. Si rien n'est précisé, prendre aujourd'hui.
- **Une plage horaire optionnelle** : si l'utilisateur dit par exemple "entre 9h et 14h", filtrer en conséquence.

Sans date précisée (ex : « fais-moi mon log »), prendre aujourd'hui sans poser de question. Ne demander que si la date donnée est vraiment ambiguë (« mardi » sans savoir lequel).

## Collecte de l'activité : le script

Tout le travail mécanique (commits, sessions Claude Code, sessions Codex CLI, fuseau horaire, découpage en blocs, durées) est fait par `scripts/timelog.py`, dans le dossier de ce skill. Le lancer depuis le dossier du projet, ne pas réécrire ces extractions à la main :

```bash
python3 <dossier de ce skill>/scripts/timelog.py                     # aujourd'hui
python3 <dossier de ce skill>/scripts/timelog.py --date 2026-05-17   # un autre jour
```

Le script est en lecture seule. Il :
- lit les commits de l'utilisateur courant (`git config user.email`) sur toutes les branches, avec les fichiers touchés ;
- retrouve les sessions Claude Code (`~/.claude/projects/`) et Codex CLI (`~/.codex/sessions/`) dont le dossier de travail est le projet courant ou un de ses sous-dossiers ;
- filtre sur les horodatages internes, pas sur la date du fichier : une session commencée la veille et reprise le jour cible compte pour ses messages du jour cible ;
- ne garde que ce que l'utilisateur a réellement tapé ou collé (pas les retours d'outils, notifications, instructions injectées), plus les commandes lancées (`/tidy`…), avec au plus 50 messages par session, chacun coupé à 400 caractères. Si un message coupé est indispensable pour comprendre un bloc, relire ce passage dans le fichier de session ;
- convertit tout en heure locale de la machine ;
- découpe en blocs (pause de plus de 90 minutes = nouveau bloc) et calcule chaque durée et le total.

Sortie :

```
PROJET /chemin/du/projet - 2026-05-17

BLOC 1 : 9h43-12h (2h17)
  [claude 09:43] message de l'utilisateur...
  [git 10:12] sujet du commit (fichiers : a.php, b.php)
  [codex 11:02] message de l'utilisateur...

BLOC 2 : 14h-16h45 (2h45)
  ...

TOTAL : 5h02
```

Les heures, durées et total du script sont à reprendre tels quels : ne pas les recalculer. Le travail de l'agent commence après : comprendre chaque bloc et le reformuler en langage client.

Si le script affiche `AUCUNE ACTIVITÉ`, le dire simplement : « Aucune activité détectée pour ce projet le [date]. »

## Blocs horaires

Un bloc = une période d'activité continue, avec au plus 90 minutes de pause entre deux événements. Le script les calcule.

Format des heures : `9h-11h30`, `14h-16h45`. Pas de minutes si pile (`9h` plutôt que `9h00`). La durée suit entre parenthèses : `9h43-12h (2h17)`, ou `45min` sous l'heure. Si la journée contient plusieurs blocs, finir par `Total journée : XhYY`. Si toute la journée tient en un seul bloc, ne pas insister sur l'horaire, mais garder la durée.

## Format de sortie

### Style général

Les logs partent dans Toggl et **sont lus par le client final**, qui n'est pas développeur. Le mode par défaut est donc : **langage compréhensible par le client, concis, sans jargon technique**.

#### Mode par défaut : pour le client

**À retirer systématiquement de la sortie** (même si présent dans les sessions ou commits) :
- **IDs, numéros de phase, références internes** : "Phase 4-4", "item 49", "template 3931", "C4", "C5", "Q1", "round 4", numéros de tickets
- **Noms de fichiers et scripts** : "qa-item-49-validate.php", "scripts/qa-phase-e-automatable.php"
- **Noms de fonctions, hooks, méta-clés, paramètres internes** : "token_set_default", "prepare_source", "_bf_stripe_account", "list_item"
- **Noms de skills, outils CLI, agents** : "confront-codex", "doc-sync", "Codex", "Claude" — les traduire par leur **intention** ("vérification avec assistance d'IA", "mise à jour de la documentation")
- **Anglicismes techniques opaques pour un non-dev** : "backfill", "cutover", "gate preflight", "snippets", "cluster", "fork", "presentment", "AS", "patches" — traduire en français courant

**À conserver** :
- Noms propres connus du client : Stripe, PayPal, Telegram, WordPress, Elementor, Outlook, etc.
- Prénoms des personnes impliquées : Julien, Sophie, etc.
- Concepts métier que le client maîtrise : membership, buy-out, Customer, formule, espace étudiant, etc.
- Termes techniques courts et lisibles intuitivement : "fix", "config", "MAJ", "deploy", "landing page", "design system"

**Exemples de traductions** (avant → après) :
| Brut technique | Version client |
|----|----|
| "13 snippets migrés vers plugin, snippets actifs prod 18→5" | "regroupement de plusieurs bouts de code épars dans une seule extension propre" |
| "fix sync du template Elementor 3931 live→staging" | "resynchro d'un gabarit de page entre la prod et l'environnement de test" |
| "validation empirique Q1 (CAD presentment OK sur compte US Standard via test API PaymentIntent)" | "confirmation que les paiements peuvent être facturés en dollars canadiens même depuis le compte américain" |
| "PayPal globalement off" | "désactivation de PayPal partout" |
| "backfill C4 _bf_stripe_account historique" | "marquage rétroactif des commandes historiques pour identifier leur compte d'origine" |
| "confront-codex round 4 Phase E pré-QA atteignant consensus absolu" | "vérification avec assistance d'IA en plusieurs passes" |
| "3 patches préventifs du fork US issus de Codex" | "3 correctifs préventifs sur le code de paiement modifié" |
| "doc-sync aligné sur consensus Phase C+D" | "mise à jour de la documentation projet" |
| "amorce Phase 4-5 cluster bf-student-area" | "amorce de la migration suivante : le module \"Espace Étudiant\"" |

#### Concision

**Un bloc Toggl doit rester court et lisible.** Quelques tâches séparées par ` - `, pas une dissertation.

- **Regrouper thématiquement** plutôt que tout énumérer. Trois sous-actions sur le même sujet → une seule mention synthétique.
- **Ne pas répéter le contexte** entre tâches d'un même bloc : si on dit "préparation des tests Stripe CA→US", ce qui suit est compris comme rattaché à ce contexte.
- **En cas de doute, plus court vaut mieux que plus long.** Le client préfère lire 2 lignes claires que 6 lignes denses.
- **Plafond mental** : si un bloc dépasse ~50 mots, c'est probablement à resserrer. Sauf bloc vraiment massif (plusieurs heures avec sujets variés).

#### Format

- **Séparateur entre tâches** : ` - ` (espace tiret espace), jamais d'em dash (`—`). Zéro em dash dans la sortie, jamais.
- Parfois ` + ` quand le lien entre deux tâches est plus fort (sujets connexes).
- **Pas de majuscule systématique** au début de chaque tâche.
- **Première personne implicite** : pas de "j'ai fait", on dit directement "finalisation de X", "mise en place de Y", "préparation de Z".
- **Pas de markdown**, pas de bullets, pas de bold. Juste du texte plat séparé par ` - `.

#### Mode "technique brut" (exception sur demande)

Si l'utilisateur précise explicitement que le log est **pour lui** ("log technique", "version brute pour moi", "garde les détails techniques", "log dev"), alors garder les IDs, noms de scripts, références de phases, noms de fonctions, etc. **Ce mode reste l'exception, jamais le défaut.**

### Template par bloc

Pour un seul bloc :

```
[heure début]-[heure fin] (durée) : tâche 1 - tâche 2 - tâche 3 - ...
```

Pour plusieurs blocs dans la journée :

```
[heure 1]-[heure 2] (durée 1) : tâche 1 - tâche 2 - ...

[heure 3]-[heure 4] (durée 2) : tâche 1 - tâche 2 - ...

Total journée : XhYY
```

Une ligne vide entre les blocs. Pas de titre, pas de markdown, pas de bullet points. Juste les lignes prêtes à être copiées-collées dans Toggl. Le total de journée vient en dernier, séparé par une ligne vide.

### Exemples d'inspiration (style cible)

#### Blocs courts (cas habituel)

- `Verif réglage Hermes et logs suite au down indiqué par Julien - diagno / correction / updates - montage cron job sur ma machine pour updates lun-mercredi - montage agent Iris et bot Telegram - configuration du skill Publer`
- `Finalisation design system - sync des données via github - création d'une landing page et upload pour sur serveur Sophie - envoi`
- `Travail de Atelier Nord : dépannage Outlook et DMARC ateliernord + travail design system avec Sophie`
- `Dev App SEO : appel avec Nadia sur les points à améliorer + fix des fields file upload en téléchargement`

#### Bloc long multi-sujets (cas plus rare, grosse session)

Référence pour un bloc qui couvre plusieurs heures avec deux fronts en parallèle (migration de module + intégration Stripe), en langage client :

> `finalisation de la migration en production d'un gros module d'affichage des cours sur boutique-fleurs.ca (regroupement de plusieurs bouts de code épars dans une seule extension propre, et resynchro d'un gabarit de page entre la prod et l'environnement de test) - préparation des tests de validation pour la migration Stripe Canada → US : récupération des réponses de Julien aux questions préparatoires, confirmation que les paiements peuvent être facturés en dollars canadiens même depuis le compte américain, désactivation de PayPal partout, marquage rétroactif des commandes historiques pour identifier leur compte d'origine, ajout d'une colonne "Compte Stripe" dans l'admin avec un filtre, et 3 correctifs préventifs sur le code de paiement modifié - vérification de tout ça avec assistance d'IA en plusieurs passes - livraison de scripts de tests automatiques - en parallèle, amorce de la migration suivante : le module "Espace Étudiant"`

Remarquer dans cet exemple :
- **Aucun ID, aucun numéro de phase, aucun nom de script, aucun nom de skill ni de fonction interne.**
- Les sous-détails techniques sont regroupés entre parenthèses ("regroupement de plusieurs bouts de code épars..."), pas énumérés à plat.
- Noms propres conservés : boutique-fleurs.ca, Stripe, PayPal, Julien.
- Concepts métier conservés : "compte Stripe", "espace étudiant", "Compte Stripe" (colonne admin).
- Ton direct, factuel, première personne implicite, séparateurs ` - ` et parfois ` + `.

#### Anti-pattern à éviter

Trop brut, illisible pour le client :

> `Phase 4-4 cutover prod cluster bf-courses-display sur boutique-fleurs.ca (13 snippets migrés vers plugin, snippets actifs prod 18→5, fix sync du template Elementor 3931 live→staging via script dédié) - Stripe CA→US : validation empirique Q1 (CAD presentment OK sur compte US Standard via test API PaymentIntent) - doc-sync aligné sur consensus Phase C+D - Phase E pré-QA livrée : PayPal globalement off, backfill C4 _bf_stripe_account historique, colonne admin C5 compte Stripe + filtre, 3 patches préventifs du fork US issus de Codex (token_set_default, list_item, prepare_source) - confront-codex round 4 Phase E pré-QA atteignant consensus absolu`

Pourquoi c'est mauvais : IDs et numéros partout ("Phase 4-4", "C4", "C5", "Q1", "round 4", "Elementor 3931"), noms de fonctions ("token_set_default"), noms de skills ("confront-codex", "doc-sync"), jargon ("cutover", "backfill", "snippets", "fork"). Le client comprend une fraction de ce qui s'est passé.

## Workflow d'exécution

1. **Vérifier le contexte** : le dossier courant doit être celui d'un projet client. Sans `.git`, prévenir que seules les sessions seront prises en compte.
2. **Déterminer la date cible** depuis la requête. Par défaut : aujourd'hui.
3. **Lancer le script** (voir « Collecte de l'activité ») avec cette date.
4. **Pour chaque bloc**, lire les messages et les commits qu'il contient, en déduire ce qui a été fait (ce que l'utilisateur a demandé, pas ce que le modèle a répondu), puis **reformuler en langage client** (voir Style général). Ne pas distinguer les agents : Claude et Codex sur le même sujet, c'est une seule tâche.
5. **Filtrer** selon la plage horaire demandée, le cas échéant.
6. **Présenter** la synthèse dans le chat, prête à copier-coller. Pas de fichier créé.

## Règles importantes

- **Jamais d'em dash (`—`)** dans la sortie. L'utilisateur déteste ça. Toujours utiliser le tiret simple `-`.
- **Ne pas inventer** d'activités. Si une session Claude Code ou Codex n'est pas claire, mieux vaut un résumé vague ("travail divers sur X") qu'une fabulation détaillée.
- **Ne pas mentionner Claude ni Codex** ni aucun nom de skill/CLI dans la sortie. C'est l'utilisateur qui a fait le travail. La synthèse est rédigée à la première personne du singulier implicite. Quand l'IA a vraiment fait partie du travail, l'écrire avec la formule « avec assistance d'IA » : « debug avec assistance d'IA », « vérification avec assistance d'IA ». Jamais le nom de l'outil, jamais « une seconde IA » ou « une deuxième IA ».
- **Mode client par défaut** : voir section Style général. Le mode technique brut est l'exception, activé uniquement sur demande explicite de l'utilisateur.
- **Pas de markdown lourd** : pas de `##`, pas de `**bold**`, pas de bullets. Juste du texte plat avec retours à la ligne entre blocs.
- **Si rien n'a été fait ce jour-là** dans ce projet (pas de commit, pas de session), le dire simplement : "Aucune activité détectée pour ce projet le [date]."
- **Demander confirmation rapide** si la date est ambiguë, mais ne pas surcharger l'utilisateur de questions — l'objectif est qu'il copie-colle vite.

## Cas limites

- **Beaucoup de petits commits rapprochés** : ne pas faire un bullet par commit. Synthétiser thématiquement (ex: ne pas dire "fix typo header - fix typo footer - fix typo nav", dire "fix de typos divers").
- **Sessions Claude Code très longues** : extraire les thèmes principaux des messages utilisateur, ne pas tout énumérer.
- **Travail purement exploratoire sans commit** : si l'utilisateur a passé une heure à débugger ou explorer sans commit final, le mentionner ("diagno / exploration sur X").
- **Plusieurs sujets dans un même bloc** : utiliser ` - ` pour séparer, ou parfois ` + ` quand le lien est plus fort (cf. exemple "dépannage Outlook et DMARC ateliernord + travail design system").

## Mode "quick" — survol multi-projets

Variante déclenchée par `/timelog quick`. Objectif : répondre à **"sur quels projets j'ai travaillé récemment ?"** — sans détail horaire, sans bloc, sans commits. Juste la liste des projets touchés, groupés par jour.

### Déclencheurs et plage

- `/timelog quick` → aujourd'hui uniquement
- `/timelog quick 7` (ou `7j`) → les 7 derniers jours, aujourd'hui inclus
- `/timelog quick YYYY-MM-DD` → un jour précis
- `/timelog quick YYYY-MM-DD..YYYY-MM-DD` → plage explicite

Formulations naturelles acceptées : "quels projets cette semaine", "survol des 15 derniers jours", "sur quoi j'ai travaillé hier"…

### Différence avec le mode par défaut

Le mode par défaut se lance **depuis un projet** et analyse ce projet seul. Le mode `quick` fait l'inverse : il scanne **tous** les projets détectés sur la machine à travers Claude Code et Codex CLI. On n'a donc pas besoin d'être dans un repo git — `/timelog quick` peut se lancer depuis n'importe quel dossier.

### Sources

Même script, avec l'option `--quick` :

```bash
python3 <dossier de ce skill>/scripts/timelog.py --quick                          # aujourd'hui
python3 <dossier de ce skill>/scripts/timelog.py --quick --days 7                 # 7 derniers jours
python3 <dossier de ce skill>/scripts/timelog.py --quick --date 2026-05-17
python3 <dossier de ce skill>/scripts/timelog.py --quick --range 2026-05-10..2026-05-17
```

Il parcourt toutes les sessions Claude Code et Codex CLI de la machine, lit le vrai dossier de travail inscrit dans chaque session, et sort une ligne par jour (`2026-05-17 : projet-a, projet-b`). **Pas de git** dans ce mode : on veut savoir où l'utilisateur *travaillait*, pas où il a *poussé du code*. Une session compte pour le jour de son premier message utilisateur, en heure locale.

Le script applique déjà les règles de nom, de tri, de dédoublonnage et d'exclusion décrites plus bas. Il reste à convertir les dates au format français court.

### Nom de projet affiché

Le **dernier segment du `cwd`** (basename), rien de plus.

Exemples :
- `/home/moi/projets/boutique-fleurs.ca` → `boutique-fleurs.ca`
- `/home/moi/projets/ma-boutique-stripe` → `ma-boutique-stripe`
- `/home/moi/projets/claude-skills` → `claude-skills`

### Format de sortie

Groupé **par jour**, ordre chronologique croissant. Les jours sans activité sont sautés silencieusement (ne pas afficher `17 juil : (rien)` sauf si l'utilisateur demande explicitement à voir les jours creux).

```
15 juil : boutique-fleurs.ca, ma-boutique-stripe
16 juil : ma-boutique-stripe
18 juil : claude-skills, ma-boutique-stripe
```

Règles :
- Date en français court : `15 juil`, `1er août`, `3 déc`. Si la plage traverse une année, ajouter l'année : `15 juil 2025`.
- Projets triés alphabétiquement dans chaque ligne.
- Séparateur entre projets : `, ` (virgule espace).
- Aucune heure, aucune durée, aucun bloc, aucune tâche, aucun commit.
- Pas de markdown, pas de bullets, pas de bold. Texte plat.

### Aucun projet détecté

```
Aucune activité détectée sur la plage [X..Y].
```

### Cas limites

- **`cwd` en dehors des chemins de projet habituels** (`/tmp`, `$HOME` nu, `~/Downloads`) : ignorer silencieusement, ce ne sont pas des projets.
- **Session à cheval sur deux jours** (commencée à 23h50, dernier message à 00h30) : la compter uniquement sur le jour de son premier message utilisateur.
- **Plusieurs sessions le même jour sur le même projet** : dédupliquer, le projet n'apparaît qu'une seule fois par jour.
- **Nom de projet dupliqué entre deux chemins différents** (rare : deux dossiers `client-x` dans des parents différents) : préciser le parent en préfixe (`Apps-coding/client-x`, `archives/client-x`) uniquement dans ce cas de collision, sinon rester sur le basename simple.
