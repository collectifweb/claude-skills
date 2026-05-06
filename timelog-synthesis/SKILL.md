---
name: timelog-synthesis
description: Génère une synthèse du travail effectué dans la journée pour un projet client, formatée en entrées de log de temps prêtes à être copiées dans Toggl ou un autre outil de time-tracking. Découpe automatiquement la journée en blocs horaires basés sur l'activité (commits git + sessions Claude Code), avec une pause de 90 minutes comme seuil entre deux blocs distincts. Utilise ce skill dès que l'utilisateur demande "log de temps", "synthèse de la journée", "résume ce que j'ai fait aujourd'hui/hier", "timelog", "time tracking", "rapport d'activité", "qu'est-ce que j'ai fait aujourd'hui", ou tape la slash command `/timelog`. À utiliser uniquement à l'intérieur d'un dossier de projet client (le repo courant).
---

# Timelog Synthesis

Génère des entrées de log de temps en français pour le projet client courant, à partir de l'activité git et des sessions Claude Code de la journée.

## Quand l'utiliser

L'utilisateur travaille comme dev freelance et logue son temps dans Toggl à la fin de la journée (ou plus tard). Il déclenche ce skill depuis le dossier d'un projet client pour obtenir une synthèse compréhensible par des clients non-techniques mais qui montre quand même la maîtrise technique.

Ce skill est lancé **uniquement** depuis un dossier de projet client. Le `cwd` au moment de l'exécution détermine quel projet analyser, point.

## Paramètres

L'utilisateur peut spécifier :
- **Une date** : "aujourd'hui" (défaut), "hier", ou une date au format `YYYY-MM-DD` ou `JJ/MM`. Si rien n'est précisé, prendre aujourd'hui.
- **Une plage horaire optionnelle** : si l'utilisateur dit par exemple "entre 9h et 14h", filtrer en conséquence.

Si la requête est ambiguë (ex: "fais-moi mon log"), demander brièvement la date avant de continuer. Sinon, foncer.

## Sources de données à inspecter

Deux sources, à combiner :

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

Exemple d'extraction rapide avec `jq` :

```bash
jq -r 'select(.type == "user") | "\(.timestamp) | \(.message.content[0:200])"' <session.jsonl>
```

Si `jq` n'est pas disponible, utiliser `python3` avec un petit script inline.

Limiter chaque session à environ 30-50 messages utilisateur extraits maximum. Si une session est gigantesque, prendre les premiers messages (qui posent le contexte) et faire un échantillonnage intelligent du reste.

## Détection des blocs horaires

Un **bloc horaire** = une période d'activité continue avec une pause maximale de **90 minutes** entre deux événements consécutifs.

Algorithme :
1. Rassembler tous les timestamps du jour : commits git + premiers/derniers messages des sessions Claude Code.
2. Trier chronologiquement.
3. Parcourir la liste : si l'écart entre deux événements consécutifs dépasse 90 minutes, ouvrir un nouveau bloc.
4. Pour chaque bloc, retenir l'heure de début (premier événement) et l'heure de fin (dernier événement).

Format des heures : `9h-11h30`, `14h-16h45`, etc. Pas de minutes si pile (`9h` plutôt que `9h00`), minutes en suffixe sinon (`11h30`).

Si toute la journée tient en un seul bloc, ne pas insister sur l'horaire — le mentionner brièvement et c'est tout.

## Format de sortie

### Style général

L'utilisateur écrit ses logs en français naturel et concis, avec ces caractéristiques :

- **Séparateur entre tâches** : ` - ` (espace tiret espace), jamais d'em dash (`—`). C'est important : zéro em dash dans la sortie, jamais.
- **Abréviations naturelles permises mais pas obligatoires** : "Verif", "diagno", "fix", "dev", "config", "MAJ"
- **Mélange français/anglais technique normal** : "fix", "upload", "deploy", "landing page", "design system" restent en anglais
- **Noms propres conservés** : prénoms de clients, noms de projets, services tiers (Outlook, DMARC, Telegram, Publer, etc.)
- **Pas de majuscule systématique** au début de chaque tâche
- **Concis mais détaillé** : on peut allonger si beaucoup de choses ont été faites dans le bloc
- **Niveau de langage** : compréhensible par un client non-dev, mais avec assez de termes techniques pour montrer la maîtrise du domaine

### Template par bloc

Pour un seul bloc :

```
[heure début]-[heure fin] : tâche 1 - tâche 2 - tâche 3 - ...
```

Pour plusieurs blocs dans la journée :

```
[heure 1]-[heure 2] : tâche 1 - tâche 2 - ...

[heure 3]-[heure 4] : tâche 1 - tâche 2 - ...
```

Une ligne vide entre les blocs. Pas de titre, pas de markdown, pas de bullet points. Juste les lignes prêtes à être copiées-collées dans Toggl.

### Exemples d'inspiration (style cible)

Voici des exemples du style de l'utilisateur (à reproduire dans la tonalité, pas à copier verbatim) :

- `Verif réglage Hermes et logs suite au down indiqué par Patrick - diagno / correction / updates - montage cron job sur ma machine pour updates lun-mercredi - montage agent Églantine et bot Telegram - configuration du skill Publer`
- `Finalisation design system - sync des données via github - création d'une landing page et upload pour sur serveur Marie-Claire - envoi`
- `Travail de TrikTrak : dépannage Outlook et DMARC laklak + travail design system avec Marie-Claire`
- `Dev App SEO : appel avec Patricia sur les points à améliorer + fix des fields file upload en téléchargement`

Remarquer : ton direct, factuel, pas de phrases complètes, séparateurs ` - ` et parfois ` + `. Reproduire cette énergie.

## Workflow d'exécution

1. **Vérifier le contexte** : confirmer que `pwd` est bien dans un dossier de projet (présence d'un `.git`). Si pas de `.git`, prévenir l'utilisateur que le skill ne fonctionnera bien qu'à la racine d'un repo client.

2. **Déterminer la date cible** depuis la requête de l'utilisateur. Par défaut : aujourd'hui.

3. **Récupérer les commits** du jour pour l'utilisateur courant.

4. **Récupérer les sessions Claude Code** du jour pour ce dossier.

5. **Construire la timeline** des événements (commits + bornes des sessions) et détecter les blocs avec le seuil de 90 min.

6. **Pour chaque bloc**, synthétiser ce qui a été fait :
   - Regarder les messages utilisateur des sessions tombant dans ce bloc (pas l'output assistant — ce qui compte c'est ce que l'utilisateur a demandé/voulu)
   - Regarder les commits du bloc et leur scope (fichiers modifiés)
   - Reformuler en langage naturel à la sauce de l'utilisateur (voir exemples)

7. **Présenter** la synthèse dans le chat, prête à copier-coller. Pas de fichier créé.

## Règles importantes

- **Jamais d'em dash (`—`)** dans la sortie. L'utilisateur déteste ça. Toujours utiliser le tiret simple `-`.
- **Ne pas inventer** d'activités. Si une session Claude Code n'est pas claire, mieux vaut un résumé vague ("travail divers sur X") qu'une fabulation détaillée.
- **Ne pas mentionner Claude** ni "j'ai aidé l'utilisateur à..." dans la synthèse. C'est l'utilisateur qui a fait le travail, point. La synthèse est rédigée à la première personne du singulier implicite (style des exemples).
- **Pas de markdown lourd** : pas de `##`, pas de `**bold**`, pas de bullets. Juste du texte plat avec retours à la ligne entre blocs.
- **Si rien n'a été fait ce jour-là** dans ce projet (pas de commit, pas de session), le dire simplement : "Aucune activité détectée pour ce projet le [date]."
- **Demander confirmation rapide** si la date est ambiguë, mais ne pas surcharger l'utilisateur de questions — l'objectif est qu'il copie-colle vite.

## Cas limites

- **Beaucoup de petits commits rapprochés** : ne pas faire un bullet par commit. Synthétiser thématiquement (ex: ne pas dire "fix typo header - fix typo footer - fix typo nav", dire "fix de typos divers").
- **Sessions Claude Code très longues** : extraire les thèmes principaux des messages utilisateur, ne pas tout énumérer.
- **Travail purement exploratoire sans commit** : si l'utilisateur a passé une heure à débugger ou explorer sans commit final, le mentionner ("diagno / exploration sur X").
- **Plusieurs sujets dans un même bloc** : utiliser ` - ` pour séparer, ou parfois ` + ` quand le lien est plus fort (cf. exemple "dépannage Outlook et DMARC laklak + travail design system").
