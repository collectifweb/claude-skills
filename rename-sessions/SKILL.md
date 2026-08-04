---
name: rename-sessions
description: Renomme en masse les sessions Claude Code d'un workspace avec un titre court et un emoji de statut, pour les retrouver d'un coup d'œil dans /resume. Trigger /rename-sessions, "renomme les sessions", "nettoie les titres de sessions", "les sessions ont des noms illisibles", "rename my sessions".
---

# rename-sessions

Les titres de sessions générés automatiquement sont longs, souvent en anglais, et ne
disent rien au premier coup d'œil : « Review Termageddon assistant security changes ».
Après trois mois de travail, la liste `/resume` devient un mur de phrases interchangeables
où plus rien ne se retrouve.

Ce skill reprend toutes les sessions d'un workspace et leur donne un titre court précédé
d'un emoji de statut, pour que la liste se lise en diagonale.

## Convention

Emoji de statut + **3 à 6 mots max**. Le titre dit ce qui a été fait, pas ce qui a été
touché.

- ✅ terminé / livré
- ⏳ en cours, ou à reprendre plus tard
- ⭐ à regarder, décision en attente
- 🔒 revue de sécurité

Quatre emojis, pas plus : au-delà, la liste cesse de se lire d'un coup d'œil et chaque
symbole perd son sens.

Une session qui n'est que le lancement d'un skill prend le nom du skill en tête, suivi de
quelques mots si nécessaire : `✅ /tidy - purge des secrets`,
`🔒 /security-review - API Axeptio`.

**Un titre déjà conforme se garde tel quel** : on ajoute l'emoji devant, on ne réécrit pas
le texte. Un titre écrit à la main porte une intention que le modèle n'a pas à corriger.

Si l'utilisateur a déjà nommé quelques sessions, lire ces titres avant de proposer quoi
que ce soit — ils révèlent sa convention réelle, qui prime sur celle décrite ici. Certains
mélangent deux langues pour rester court : c'est un choix, pas une incohérence à réparer.

## Mécanisme

Le titre affiché vient de la **dernière** ligne `type: "custom-title"` du fichier
`~/.claude/projects/<workspace-encodé>/<session-id>.jsonl`. Renommer revient donc à
ajouter une ligne en fin de fichier :

```json
{"type":"custom-title","customTitle":"✅ Fix erreur feuille de route","sessionId":"<uuid>"}
```

L'opération est **purement additive** : rien n'est écrasé, une erreur se corrige avec une
ligne de plus. Les lignes `ai-title` écrites ensuite ne reprennent pas le dessus.

Le `<workspace-encodé>` est le chemin absolu du projet avec `/` et `_` remplacés par `-`
(`/home/moi/Apps/mon-projet` → `-home-moi-Apps-mon-projet`). Vérifier que le dossier
existe avant d'aller plus loin plutôt que de supposer l'encodage.

## Déroulé

**1. Inventaire.** Pour chaque `.jsonl` du dossier workspace, extraire : date de dernière
modification, dernier `custom-title` (le titre actuel), dernier `ai-title` (le titre
auto-généré), premier message utilisateur, nombre de messages. Le premier message suffit
presque toujours à comprendre le sujet ; n'aller lire plus loin que si le titre reste flou.

Trier par date et repérer les familles :

- Les revues de sécurité automatiques — premier message commençant par « Review this
  change for security vulnerabilities ». Elles peuvent représenter la moitié de la liste.
- Les lancements de skill — premier message commençant par « Base directory for this
  skill ».

Dans une famille, différencier les sessions par leur sujet réel, sinon vingt titres
identiques ne valent pas mieux que vingt titres auto-générés. Pour les revues de sécurité,
les fichiers listés dans le prompt donnent le sujet. Quand deux sessions restent
réellement jumelles, les numéroter `(2)`, `(3)`.

**2. Statut.** Croiser avec le CLAUDE.md du projet et le journal git pour savoir ce qui a
réellement été livré. Ne pas forcer les quatre emojis : si aucune session ne mérite ⭐, ne
pas en inventer une. Dans le doute entre ✅ et ⏳, demander plutôt que de trancher seul —
un ⏳ posé à tort sur du travail terminé est un faux signal qui coûte du temps plus tard.

**3. Sauvegarde.** Écrire l'état courant (fichier → titre actuel, nombre de lignes) dans
un JSON du scratchpad avant toute écriture.

**4. Script.** Une table `préfixe d'id → titre`, et un contrôle de couverture qui
**s'arrête** si une session du dossier n'a pas de titre prévu, ou si un titre vise une
session inexistante. Passe à blanc d'abord, application seulement ensuite.

**5. Vérification.** Relire tous les fichiers : chaque session a bien le nouveau titre
comme dernier `custom-title`, et aucune ligne JSON n'est devenue illisible.

## Nommer au fil de l'eau

Le rattrapage en masse ne devrait avoir lieu qu'une fois. Pour que les sessions suivantes
naissent avec un bon titre, proposer d'ajouter la règle du README au `~/.claude/CLAUDE.md`
de l'utilisateur.

Le principe, si la question se pose : **on ne peut pas détecter la fin d'une session** — le
modèle ne tourne plus quand la fenêtre se ferme. Donc nommer **tôt**, en ⏳, dès que le
sujet est clair, puis affiner aux jalons (déploiement vérifié, correctif prouvé → ✅). Une
session coupée net garde ainsi un titre juste, et le ⏳ qui subsiste dit quelque chose de
vrai : ce travail-là n'a pas été bouclé.

Ne jamais identifier la session courante en prenant le `.jsonl` le plus récemment modifié :
plusieurs sessions tournent souvent en parallèle. L'identifiant de la session courante est
le nom du dossier parent du scratchpad indiqué dans le prompt système.

## À rapporter

- Le compte exact renommé, et la confirmation qu'aucun fichier n'est abîmé.
- Toute déviation de la convention, avec sa raison — jamais trancher en silence sur un
  titre écrit à la main.
- Qu'il faut parfois rouvrir `/resume` pour que Claude Code relise les fichiers.
- Que rien n'est commité : ces fichiers vivent dans `~/.claude/`, hors dépôt.
