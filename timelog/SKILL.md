---
name: timelog
description: Génère synthèse de journée (Toggl) — blocs basés sur commits git + sessions Claude/Codex (seuil 90 min). Variante /timelog quick : survol multi-jours multi-projets sans détail horaire, réponse à "sur quels projets j'ai travaillé". Trigger /timelog, /timelog quick, "log de temps", "synthèse journée", "résume ce que j'ai fait", "time tracking", "quels projets cette semaine", "sur quels projets j'ai travaillé".
---

# Timelog

Génère des entrées de log de temps en français pour le projet client courant, à partir de l'activité git, des sessions Claude Code **et des sessions Codex CLI** de la journée.

**Compatible Claude Code et Codex CLI** : ce skill est installé aux deux endroits (symlinks depuis le monorepo `claude-skills`) et fonctionne identiquement quel que soit l'agent qui le lance. Les deux types de sessions sont fusionnés dans la même timeline.

## Quand l'utiliser

L'utilisateur travaille comme dev freelance et logue son temps dans Toggl à la fin de la journée (ou plus tard). Il déclenche ce skill depuis le dossier d'un projet client pour obtenir une synthèse compréhensible par des clients non-techniques mais qui montre quand même la maîtrise technique.

Ce skill est lancé **uniquement** depuis un dossier de projet client. Le `cwd` au moment de l'exécution détermine quel projet analyser, point.

## Paramètres

L'utilisateur peut spécifier :
- **Une date** : "aujourd'hui" (défaut), "hier", ou une date au format `YYYY-MM-DD` ou `JJ/MM`. Si rien n'est précisé, prendre aujourd'hui.
- **Une plage horaire optionnelle** : si l'utilisateur dit par exemple "entre 9h et 14h", filtrer en conséquence.

Si la requête est ambiguë (ex: "fais-moi mon log"), demander brièvement la date avant de continuer. Sinon, foncer.

## Sources de données à inspecter

Trois sources, à combiner :

### 1. Historique git du repo courant

Récupérer les commits du jour de l'utilisateur courant :

```bash
git log --since="<date> 00:00" --until="<date> 23:59" --author="$(git config user.email)" --pretty=format:"%H|%ai|%s%n%b---END---" --reverse
```

Pour chaque commit, récupérer aussi les fichiers touchés (utile pour comprendre la nature du travail) :

```bash
git show --stat --format="" <commit-hash>
```

Note : les commits sont une excellente source de timestamps fiables pour borner les blocs horaires.

### 2. Sessions Claude Code du jour

Les conversations Claude Code sont stockées dans `~/.claude/projects/<chemin-projet-encodé>/*.jsonl`. Le chemin du projet courant est encodé en remplaçant les `/` par des `-` (ex: `/home/user/clients/acme` devient `-home-user-clients-acme`).

Repérer le bon dossier :

```bash
PROJECT_DIR=$(pwd | sed 's|/|-|g')
SESSIONS_DIR="$HOME/.claude/projects/${PROJECT_DIR}"
ls -la "$SESSIONS_DIR" 2>/dev/null
```

Si le dossier existe, lister les fichiers `.jsonl` modifiés le jour cible :

```bash
find "$SESSIONS_DIR" -name "*.jsonl" -newermt "<date>" ! -newermt "<date+1>"
```

Pour chaque session du jour, extraire le contenu pertinent. Les `.jsonl` contiennent des lignes JSON avec des messages utilisateur et assistant. Pour rester efficace en tokens, extraire uniquement :
- Les messages utilisateur (`type: "user"`) — ils décrivent ce que l'utilisateur a demandé
- Le premier et le dernier message pour borner la session temporellement (`timestamp`)

**⚠️ Conversion de fuseau horaire obligatoire** : les timestamps dans les `.jsonl` sont en **UTC**. Il faut les convertir en heure locale (America/Toronto = UTC-4 en été, UTC-5 en hiver) avant de calculer les blocs horaires et d'afficher les heures. Les timestamps git (`%ai`) sont eux déjà en heure locale (ils incluent l'offset `-0400` ou `-0500`). Ne jamais afficher une heure UTC brute dans le log — ça décalerait les blocs de 4-5 heures.

Pour convertir proprement en Python :

```python
from datetime import datetime, timezone, timedelta
import re

def utc_to_local(ts_str):
    # Parse ISO 8601 UTC timestamp from .jsonl (e.g. "2026-05-11T18:45:49.560Z")
    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    # Convert to America/Toronto (approximation: use fixed offset based on DST)
    # EDT = UTC-4 (mid-March to early Nov), EST = UTC-5 (rest of year)
    local_offset = timedelta(hours=-4)  # adjust to -5 in winter
    return dt + local_offset
```

Ou plus simplement, utiliser `python3 -c "from datetime import datetime, timedelta; ..."` en inline.

Exemple d'extraction rapide avec `jq` :

```bash
jq -r 'select(.type == "user") | "\(.timestamp) | \(.message.content[0:200])"' <session.jsonl>
```

Si `jq` n'est pas disponible, utiliser `python3` avec un petit script inline.

Limiter chaque session à environ 30-50 messages utilisateur extraits maximum. Si une session est gigantesque, prendre les premiers messages (qui posent le contexte) et faire un échantillonnage intelligent du reste.

### 3. Sessions Codex CLI du jour

L'utilisateur travaille aussi avec **Codex CLI** (`codex` en ligne de commande). Les sessions Codex sont stockées dans `~/.codex/sessions/YYYY/MM/DD/*.jsonl` (arborescence par année/mois/jour, avec un fichier `.jsonl` par session).

```bash
DATE_PATH=$(date -d "<date>" "+%Y/%m/%d")   # ex: 2026/05/17
CODEX_DIR="$HOME/.codex/sessions/$DATE_PATH"
ls "$CODEX_DIR"/*.jsonl 2>/dev/null
```

**Important** : contrairement aux sessions Claude Code (déjà rangées par projet via le nom du dossier), les sessions Codex sont rangées **uniquement par date**, pas par projet. Il faut filtrer par `cwd` :

- La **première ligne** de chaque `.jsonl` est un événement `session_meta` dont `payload.cwd` indique le répertoire de travail au lancement de la session.
- Ne retenir que les sessions dont `payload.cwd == $(pwd)` (ou un sous-dossier).

Exemple Python inline pour filtrer et extraire :

```python
import json, os
from pathlib import Path

pwd = os.getcwd()
session_dir = Path.home() / ".codex/sessions/2026/05/17"
matching = []
for jsonl in session_dir.glob("*.jsonl"):
    with open(jsonl) as f:
        first = json.loads(f.readline())
    if first.get("type") == "session_meta":
        cwd = first["payload"].get("cwd", "")
        if cwd == pwd or cwd.startswith(pwd + "/"):
            matching.append(jsonl)
```

**Format des événements** dans un `.jsonl` Codex :
- `type: "session_meta"` (1 par fichier, en tête) — métadonnées avec `cwd`, branche git, modèle, etc.
- `type: "response_item"` avec `payload.type: "message"` et `payload.role: "user"` — messages utilisateur (à extraire)
- `type: "response_item"` avec `payload.role: "assistant"` — réponses du modèle (à ignorer)
- `type: "event_msg"` — événements internes (à ignorer)

**Filtrage indispensable des messages user** : les premiers messages user injectés par Codex sont des messages système (instructions AGENTS.md, balises de permissions, etc.) qui commencent par `<` ou `# AGENTS`. Les exclure pour ne garder que les vraies demandes humaines :

```python
for line in open(jsonl):
    d = json.loads(line)
    if d.get("type") != "response_item": continue
    p = d.get("payload", {})
    if p.get("type") != "message" or p.get("role") != "user": continue
    for c in p.get("content", []):
        txt = c.get("text", "")
        if not txt or txt.startswith("<") or txt.startswith("# AGENTS"): continue
        if len(txt) < 5: continue
        print(d["timestamp"], "|", txt[:200])
```

**Timestamps Codex aussi en UTC** : même conversion America/Toronto que pour Claude Code (voir code plus haut).

**Indication "via Codex" dans la synthèse** : si une portion notable du travail d'un bloc vient d'une session Codex, le mentionner discrètement si pertinent (ex: `... - debug avec Codex sur la migration Stripe`). Ne pas surcharger : si les deux agents ont travaillé sur le même sujet, fusionner sans préciser l'agent.

Mêmes limites que pour Claude : 30-50 messages user max par session.

## Détection des blocs horaires

Un **bloc horaire** = une période d'activité continue avec une pause maximale de **90 minutes** entre deux événements consécutifs.

Algorithme :
1. Rassembler tous les timestamps du jour : commits git + premiers/derniers messages des sessions Claude Code + premiers/derniers messages user des sessions Codex (filtrées par `cwd`).
2. Trier chronologiquement.
3. Parcourir la liste : si l'écart entre deux événements consécutifs dépasse 90 minutes, ouvrir un nouveau bloc.
4. Pour chaque bloc, retenir l'heure de début (premier événement) et l'heure de fin (dernier événement).

Format des heures : `9h-11h30`, `14h-16h45`, etc. Pas de minutes si pile (`9h` plutôt que `9h00`), minutes en suffixe sinon (`11h30`).

**Toujours afficher la durée du bloc entre parenthèses** juste après la plage horaire, au format `2h17` ou `45min` si moins d'une heure. Exemple : `9h43-12h (2h17) : ...`. Calculer la durée à partir de l'heure de début et de fin du bloc (pas la somme des événements).

À la fin de la sortie, si la journée contient plusieurs blocs, ajouter une ligne `Total journée : XhYY` avec la somme des durées des blocs. Si un seul bloc, pas besoin du total.

Si toute la journée tient en un seul bloc, ne pas insister sur l'horaire — le mentionner brièvement et c'est tout (mais garder la durée entre parenthèses).

## Format de sortie

### Style général

Les logs partent dans Toggl et **sont lus par le client final**, qui n'est pas développeur. Le mode par défaut est donc : **langage compréhensible par le client, concis, sans jargon technique**.

#### Mode par défaut : pour le client

**À retirer systématiquement de la sortie** (même si présent dans les sessions ou commits) :
- **IDs, numéros de phase, références internes** : "Phase 4-4", "item 49", "template 3931", "C4", "C5", "Q1", "round 4", numéros de tickets
- **Noms de fichiers et scripts** : "qa-item-49-validate.php", "scripts/qa-phase-e-automatable.php"
- **Noms de fonctions, hooks, méta-clés, paramètres internes** : "token_set_default", "prepare_source", "_ejardin_stripe_account", "list_item"
- **Noms de skills, outils CLI, agents** : "confront-codex", "doc-sync", "Codex", "Claude" — les traduire par leur **intention** ("double-vérification par une seconde IA", "mise à jour de la documentation")
- **Anglicismes techniques opaques pour un non-dev** : "backfill", "cutover", "gate preflight", "snippets", "cluster", "fork", "presentment", "AS", "patches" — traduire en français courant

**À conserver** :
- Noms propres connus du client : Stripe, PayPal, Telegram, WordPress, Elementor, Outlook, etc.
- Prénoms des personnes impliquées : Patrick, Marie-Claire, etc.
- Concepts métier que le client maîtrise : membership, buy-out, Customer, formule, espace étudiant, etc.
- Termes techniques courts et lisibles intuitivement : "fix", "config", "MAJ", "deploy", "landing page", "design system"

**Exemples de traductions** (avant → après) :
| Brut technique | Version client |
|----|----|
| "13 snippets migrés vers plugin, snippets actifs prod 18→5" | "regroupement de plusieurs bouts de code épars dans une seule extension propre" |
| "fix sync du template Elementor 3931 live→staging" | "resynchro d'un gabarit de page entre la prod et l'environnement de test" |
| "validation empirique Q1 (CAD presentment OK sur compte US Standard via test API PaymentIntent)" | "confirmation que les paiements peuvent être facturés en dollars canadiens même depuis le compte américain" |
| "PayPal globalement off" | "désactivation de PayPal partout" |
| "backfill C4 _ejardin_stripe_account historique" | "marquage rétroactif des commandes historiques pour identifier leur compte d'origine" |
| "confront-codex round 4 Phase E pré-QA atteignant consensus absolu" | "double-vérification par une seconde IA en plusieurs passes, consensus atteint" |
| "3 patches préventifs du fork US issus de Codex" | "3 correctifs préventifs sur le code de paiement modifié" |
| "doc-sync aligné sur consensus Phase C+D" | "mise à jour de la documentation projet" |
| "amorce Phase 4-5 cluster ejardin-student-area" | "amorce de la migration suivante : le module \"Espace Étudiant\"" |

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

- `Verif réglage Hermes et logs suite au down indiqué par Patrick - diagno / correction / updates - montage cron job sur ma machine pour updates lun-mercredi - montage agent Églantine et bot Telegram - configuration du skill Publer`
- `Finalisation design system - sync des données via github - création d'une landing page et upload pour sur serveur Marie-Claire - envoi`
- `Travail de TrikTrak : dépannage Outlook et DMARC laklak + travail design system avec Marie-Claire`
- `Dev App SEO : appel avec Patricia sur les points à améliorer + fix des fields file upload en téléchargement`

#### Bloc long multi-sujets (cas plus rare, grosse session)

Référence pour un bloc qui couvre plusieurs heures avec deux fronts en parallèle (migration de module + intégration Stripe), en langage client :

> `finalisation de la migration en production d'un gros module d'affichage des cours sur ejardin.ca (regroupement de plusieurs bouts de code épars dans une seule extension propre, et resynchro d'un gabarit de page entre la prod et l'environnement de test) - préparation des tests de validation pour la migration Stripe Canada → US : récupération des réponses de Patrick aux questions préparatoires, confirmation que les paiements peuvent être facturés en dollars canadiens même depuis le compte américain, désactivation de PayPal partout, marquage rétroactif des commandes historiques pour identifier leur compte d'origine, ajout d'une colonne "Compte Stripe" dans l'admin avec un filtre, et 3 correctifs préventifs sur le code de paiement modifié - double-vérification de tout ça par une seconde IA en plusieurs passes, consensus atteint - livraison de scripts de tests automatiques - en parallèle, amorce de la migration suivante : le module "Espace Étudiant"`

Remarquer dans cet exemple :
- **Aucun ID, aucun numéro de phase, aucun nom de script, aucun nom de skill ni de fonction interne.**
- Les sous-détails techniques sont regroupés entre parenthèses ("regroupement de plusieurs bouts de code épars..."), pas énumérés à plat.
- Noms propres conservés : ejardin.ca, Stripe, PayPal, Patrick.
- Concepts métier conservés : "compte Stripe", "espace étudiant", "Compte Stripe" (colonne admin).
- Ton direct, factuel, première personne implicite, séparateurs ` - ` et parfois ` + `.

#### Anti-pattern à éviter

Trop brut, illisible pour le client :

> `Phase 4-4 cutover prod cluster ejardin-courses-display sur ejardin.ca (13 snippets migrés vers plugin, snippets actifs prod 18→5, fix sync du template Elementor 3931 live→staging via script dédié) - Stripe CA→US : validation empirique Q1 (CAD presentment OK sur compte US Standard via test API PaymentIntent) - doc-sync aligné sur consensus Phase C+D - Phase E pré-QA livrée : PayPal globalement off, backfill C4 _ejardin_stripe_account historique, colonne admin C5 compte Stripe + filtre, 3 patches préventifs du fork US issus de Codex (token_set_default, list_item, prepare_source) - confront-codex round 4 Phase E pré-QA atteignant consensus absolu`

Pourquoi c'est mauvais : IDs et numéros partout ("Phase 4-4", "C4", "C5", "Q1", "round 4", "Elementor 3931"), noms de fonctions ("token_set_default"), noms de skills ("confront-codex", "doc-sync"), jargon ("cutover", "backfill", "snippets", "fork"). Le client comprend une fraction de ce qui s'est passé.

## Workflow d'exécution

1. **Vérifier le contexte** : confirmer que `pwd` est bien dans un dossier de projet (présence d'un `.git`). Si pas de `.git`, prévenir l'utilisateur que le skill ne fonctionnera bien qu'à la racine d'un repo client.

2. **Déterminer la date cible** depuis la requête de l'utilisateur. Par défaut : aujourd'hui.

3. **Récupérer les commits** du jour pour l'utilisateur courant.

4. **Récupérer les sessions Claude Code** du jour pour ce dossier (via le chemin encodé dans `~/.claude/projects/`).

5. **Récupérer les sessions Codex CLI** du jour, en filtrant par `cwd == $(pwd)` (les sessions Codex sont rangées par date, pas par projet — il FAUT filtrer).

6. **Construire la timeline** des événements (commits + bornes des sessions Claude + bornes des sessions Codex) et détecter les blocs avec le seuil de 90 min.

7. **Pour chaque bloc**, synthétiser ce qui a été fait :
   - Regarder les messages utilisateur des sessions Claude tombant dans ce bloc
   - Regarder les messages utilisateur des sessions Codex tombant dans ce bloc (mêmes règles : on regarde ce que l'utilisateur a demandé, pas ce que le modèle a répondu)
   - Regarder les commits du bloc et leur scope (fichiers modifiés)
   - **Reformuler en langage client** (voir section Style général) : sortir le jargon technique, garder les noms propres et les concepts métier. Fusionner sans distinguer l'agent — ne jamais mentionner "Claude" ou "Codex" par défaut, juste l'intention ("double-vérification par une seconde IA" si vraiment pertinent).

8. **Présenter** la synthèse dans le chat, prête à copier-coller. Pas de fichier créé.

## Règles importantes

- **Jamais d'em dash (`—`)** dans la sortie. L'utilisateur déteste ça. Toujours utiliser le tiret simple `-`.
- **Ne pas inventer** d'activités. Si une session Claude Code ou Codex n'est pas claire, mieux vaut un résumé vague ("travail divers sur X") qu'une fabulation détaillée.
- **Ne pas mentionner Claude ni Codex** ni aucun nom de skill/CLI dans la sortie. C'est l'utilisateur qui a fait le travail. La synthèse est rédigée à la première personne du singulier implicite. Quand un outil d'IA a vraiment fait partie du travail (ex: review croisée), traduire par l'intention ("double-vérification par une seconde IA"), jamais par le nom de l'outil.
- **Mode client par défaut** : voir section Style général. Le mode technique brut est l'exception, activé uniquement sur demande explicite de l'utilisateur.
- **Pas de markdown lourd** : pas de `##`, pas de `**bold**`, pas de bullets. Juste du texte plat avec retours à la ligne entre blocs.
- **Si rien n'a été fait ce jour-là** dans ce projet (pas de commit, pas de session), le dire simplement : "Aucune activité détectée pour ce projet le [date]."
- **Demander confirmation rapide** si la date est ambiguë, mais ne pas surcharger l'utilisateur de questions — l'objectif est qu'il copie-colle vite.

## Cas limites

- **Beaucoup de petits commits rapprochés** : ne pas faire un bullet par commit. Synthétiser thématiquement (ex: ne pas dire "fix typo header - fix typo footer - fix typo nav", dire "fix de typos divers").
- **Sessions Claude Code très longues** : extraire les thèmes principaux des messages utilisateur, ne pas tout énumérer.
- **Travail purement exploratoire sans commit** : si l'utilisateur a passé une heure à débugger ou explorer sans commit final, le mentionner ("diagno / exploration sur X").
- **Plusieurs sujets dans un même bloc** : utiliser ` - ` pour séparer, ou parfois ` + ` quand le lien est plus fort (cf. exemple "dépannage Outlook et DMARC laklak + travail design system").

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

- **Sessions Claude Code** : parcourir tous les sous-dossiers de `~/.claude/projects/`. Pour chaque dossier, repérer les `.jsonl` avec au moins un message utilisateur dans la plage cible. Le vrai `cwd` du projet se trouve dans le champ `cwd` **à l'intérieur** des lignes du `.jsonl` (le nom du dossier encode `/` en `-` et devient ambigu si le vrai chemin contient déjà des `-`, donc on lit toujours le champ interne, jamais le nom du dossier).
- **Sessions Codex CLI** : pour chaque jour de la plage, parcourir `~/.codex/sessions/YYYY/MM/DD/*.jsonl`. Pour chaque fichier, lire la première ligne (`session_meta`) et récupérer `payload.cwd`.
- **Pas de git** dans ce mode. Le survol vient uniquement des sessions AI, jamais des commits — on veut savoir où l'utilisateur *travaillait*, pas où il a *poussé du code*.

Une session compte pour le jour de son **premier message utilisateur** (heure locale America/Toronto — convertir depuis UTC comme pour le mode par défaut). Filtrer les faux messages utilisateur côté Codex (ceux qui commencent par `<` ou `# AGENTS`) avant d'en tirer le premier timestamp.

### Nom de projet affiché

Le **dernier segment du `cwd`** (basename), rien de plus.

Exemples :
- `/home/alexandre/Apps-coding/ejardin.ca` → `ejardin.ca`
- `/home/alexandre/Apps-coding/ma-boutique-stripe` → `ma-boutique-stripe`
- `/home/alexandre/Apps-coding/claude-skills` → `claude-skills`

### Format de sortie

Groupé **par jour**, ordre chronologique croissant. Les jours sans activité sont sautés silencieusement (ne pas afficher `17 juil : (rien)` sauf si l'utilisateur demande explicitement à voir les jours creux).

```
15 juil : ejardin.ca, ma-boutique-stripe
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
